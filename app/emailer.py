"""SMTP-уведомления менеджеру о новых заявках."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import Settings
from app.models import LeadRequest


class EmailNotificationError(RuntimeError):
    """Ошибка отправки SMTP-уведомления."""


def send_lead_email(settings: Settings, lead: LeadRequest, lead_id: int) -> None:
    """Отправляет менеджеру письмо о новой заявке."""
    if not settings.smtp_configured:
        raise EmailNotificationError("SMTP не настроен.")

    message = EmailMessage()
    message["Subject"] = f"Новая заявка: {lead.name}"
    message["From"] = settings.smtp_from
    message["To"] = settings.smtp_to
    message.set_content(
        "\n".join(
            [
                f"Новая заявка: #{lead_id}",
                f"Имя: {lead.name}",
                f"Контакт: {lead.contact}",
                f"Источник: {lead.source}",
                f"Комментарий: {lead.comment}",
            ]
        )
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username and settings.smtp_password:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
    except OSError as exc:
        raise EmailNotificationError(str(exc)) from exc
    except smtplib.SMTPException as exc:
        raise EmailNotificationError(str(exc)) from exc
