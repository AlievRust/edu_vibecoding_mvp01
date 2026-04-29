"""Нормализация данных, по которым сервис ищет дубли заявок."""

import re


class PhoneNormalizationError(ValueError):
    """Ошибка нормализации телефона для дедупликации."""


def normalize_name(name: str) -> str:
    """Возвращает имя в формате для сравнения дублей."""
    normalized = name.strip().lower()
    return normalized or "без имени"


def normalize_phone(phone: str) -> str:
    """Приводит российский телефон к формату `+7XXXXXXXXXX`.

    Поддерживаются привычные варианты ввода:
    `+79990000000`, `89990000000`, `79990000000`, `9990000000`,
    а также записи с пробелами, скобками и дефисами.
    """
    digits = re.sub(r"\D", "", phone)

    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits

    if len(digits) != 11 or not digits.startswith("7"):
        raise PhoneNormalizationError(
            "Телефон должен быть российским номером в формате +7XXXXXXXXXX."
        )

    return f"+{digits}"

