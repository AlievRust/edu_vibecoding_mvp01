"""Тесты API приема заявок."""

import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def make_settings(tmp_path: Path, database_name: str = "leads.db") -> Settings:
    """Создает изолированные настройки для одного теста."""
    return Settings(
        database_path=tmp_path / database_name,
        events_log_path=tmp_path / "events.log",
        smtp_host=None,
        smtp_port=587,
        smtp_username=None,
        smtp_password=None,
        smtp_from=None,
        smtp_to=None,
        smtp_use_tls=True,
    )


def test_post_lead_saves_new_lead(tmp_path: Path) -> None:
    """Новая заявка сохраняется в SQLite и фиксируется в UTF-8 логе."""
    settings = make_settings(tmp_path)
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post(
            "/lead",
            json={
                "name": "Ирина",
                "contact": "+79990000000",
                "source": "landing",
                "comment": "Хочу консультацию",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "created": True,
        "message": "Заявка принята и сохранена.",
    }

    with sqlite3.connect(settings.database_path) as connection:
        row = connection.execute(
            "SELECT name, contact, normalized_name, normalized_contact FROM leads"
        ).fetchone()

    assert row == ("Ирина", "+79990000000", "ирина", "+79990000000")
    log_text = settings.events_log_path.read_text(encoding="utf-8")
    assert "New lead saved: 1." in log_text
    assert "Email notification skipped for lead 1" in log_text


def test_post_lead_returns_existing_id_for_duplicate(tmp_path: Path) -> None:
    """Дубль по имени и нормализованному телефону не создает новую строку."""
    settings = make_settings(tmp_path)
    app = create_app(settings)

    with TestClient(app) as client:
        first_response = client.post(
            "/lead",
            json={"name": "Ирина", "contact": "+79990000000"},
        )
        duplicate_response = client.post(
            "/lead",
            json={"name": " ирина ", "contact": "8 (999) 000-00-00"},
        )

    assert first_response.status_code == 200
    assert duplicate_response.status_code == 200
    assert duplicate_response.json() == {
        "id": 1,
        "created": False,
        "message": "Дубль заявки уже есть в базе.",
    }

    with sqlite3.connect(settings.database_path) as connection:
        lead_count = connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0]

    assert lead_count == 1
    assert "Duplicate lead skipped: 1." in settings.events_log_path.read_text(
        encoding="utf-8"
    )


def test_post_lead_rejects_empty_contact(tmp_path: Path) -> None:
    """Пустой contact возвращает HTTP 400."""
    app = create_app(make_settings(tmp_path))

    with TestClient(app) as client:
        response = client.post("/lead", json={"name": "Павел", "contact": ""})

    assert response.status_code == 400
    assert "Некорректный JSON" in response.json()["detail"]


def test_post_lead_rejects_unsupported_phone(tmp_path: Path) -> None:
    """Неподдерживаемый телефон возвращает HTTP 400 с понятным текстом."""
    app = create_app(make_settings(tmp_path))

    with TestClient(app) as client:
        response = client.post("/lead", json={"name": "Сергей", "contact": "+123"})

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Телефон должен быть российским номером в формате +7XXXXXXXXXX."
    }


def test_post_lead_returns_500_when_database_is_unavailable(tmp_path: Path) -> None:
    """Недоступная SQLite-база возвращает HTTP 500 и пишет событие в лог."""
    database_path = tmp_path / "not_a_database"
    database_path.mkdir()
    settings = make_settings(tmp_path, database_name=database_path.name)
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.post(
            "/lead",
            json={"name": "Мария", "contact": "+79992223344"},
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "База данных временно недоступна."}
    assert "Database error while saving lead" in settings.events_log_path.read_text(
        encoding="utf-8"
    )
