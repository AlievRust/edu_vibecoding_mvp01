"""Работа с SQLite: схема, вставка заявок и поиск дублей."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.models import LeadRequest


@dataclass(frozen=True)
class StoredLead:
    """Результат сохранения или поиска существующей заявки."""

    id: int
    created: bool


def connect(database_path: Path) -> sqlite3.Connection:
    """Открывает SQLite-соединение с удобным row factory."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path: Path) -> None:
    """Создает таблицу заявок и уникальный индекс для дедупликации."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                source TEXT NOT NULL,
                comment TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                normalized_contact TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_dedup
            ON leads (normalized_name, normalized_contact)
            """
        )
        connection.commit()


def save_lead(
    database_path: Path,
    lead: LeadRequest,
    normalized_name: str,
    normalized_contact: str,
) -> StoredLead:
    """Сохраняет новую заявку или возвращает существующую при дубле."""
    created_at = datetime.now(UTC).isoformat()

    with connect(database_path) as connection:
        try:
            cursor = connection.execute(
                """
                INSERT INTO leads (
                    created_at,
                    name,
                    contact,
                    source,
                    comment,
                    normalized_name,
                    normalized_contact
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    lead.name,
                    lead.contact,
                    lead.source,
                    lead.comment,
                    normalized_name,
                    normalized_contact,
                ),
            )
            connection.commit()
            return StoredLead(id=int(cursor.lastrowid), created=True)
        except sqlite3.IntegrityError:
            existing = find_duplicate(connection, normalized_name, normalized_contact)
            if existing is None:
                raise
            return StoredLead(id=existing, created=False)


def find_duplicate(
    connection: sqlite3.Connection,
    normalized_name: str,
    normalized_contact: str,
) -> int | None:
    """Ищет существующую заявку по ключу дедупликации."""
    row = connection.execute(
        """
        SELECT id
        FROM leads
        WHERE normalized_name = ? AND normalized_contact = ?
        """,
        (normalized_name, normalized_contact),
    ).fetchone()
    if row is None:
        return None
    return int(row["id"])
