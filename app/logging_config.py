"""Простое UTF-8 логирование событий в файл."""

from datetime import UTC, datetime
from pathlib import Path


def write_event(log_path: Path, message: str) -> None:
    """Добавляет одну строку события в UTF-8 лог."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).isoformat()
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {message}\n")

