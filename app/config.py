"""Настройки приложения из `.env` и переменных окружения."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env_file(env_path: Path) -> None:
    """Загружает простые `KEY=value` пары из `.env`, не перетирая окружение."""
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def parse_bool(value: str | None, default: bool = True) -> bool:
    """Преобразует строковое значение `.env` в `bool`."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "да"}


@dataclass(frozen=True)
class Settings:
    """Набор настроек, нужных сервису во время запроса."""

    database_path: Path
    events_log_path: Path
    smtp_host: str | None
    smtp_port: int
    smtp_username: str | None
    smtp_password: str | None
    smtp_from: str | None
    smtp_to: str | None
    smtp_use_tls: bool

    @property
    def smtp_configured(self) -> bool:
        """Проверяет, достаточно ли настроек для SMTP-отправки."""
        return bool(self.smtp_host and self.smtp_from and self.smtp_to)


def get_settings() -> Settings:
    """Возвращает настройки приложения с учетом `.env`."""
    load_env_file(PROJECT_ROOT / ".env")

    database_path = Path(os.getenv("DATABASE_PATH", PROJECT_ROOT / "leads.db"))
    events_log_path = Path(os.getenv("EVENTS_LOG_PATH", PROJECT_ROOT / "events.log"))

    return Settings(
        database_path=database_path,
        events_log_path=events_log_path,
        smtp_host=os.getenv("SMTP_HOST") or None,
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME") or None,
        smtp_password=os.getenv("SMTP_PASSWORD") or None,
        smtp_from=os.getenv("SMTP_FROM") or None,
        smtp_to=os.getenv("SMTP_TO") or None,
        smtp_use_tls=parse_bool(os.getenv("SMTP_USE_TLS"), default=True),
    )

