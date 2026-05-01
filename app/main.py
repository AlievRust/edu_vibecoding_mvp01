"""FastAPI-приложение для приема заявок через webhook."""

from __future__ import annotations

import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.database import init_db, save_lead
from app.deduplication import (
    PhoneNormalizationError,
    normalize_name,
    normalize_phone,
)
from app.emailer import EmailNotificationError, send_lead_email
from app.logging_config import write_event
from app.models import LeadRequest, LeadResponse


class UTF8JSONResponse(JSONResponse):
    """JSON-ответ с явным UTF-8 charset для старых клиентов Windows."""

    media_type = "application/json; charset=utf-8"


def create_app(settings: Settings | None = None) -> FastAPI:
    """Создает приложение и привязывает настройки к `app.state`."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        application.state.settings = settings or get_settings()
        yield

    application = FastAPI(
        title="Lead Webhook MVP",
        description="Учебный сервис для приема и сохранения заявок.",
        version="0.1.0",
        lifespan=lifespan,
        default_response_class=UTF8JSONResponse,
    )

    @application.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> UTF8JSONResponse:
        """Возвращает HTTP 400 вместо стандартного 422 для ошибок запроса."""
        return UTF8JSONResponse(
            status_code=400,
            content=jsonable_encoder({
                "detail": "Некорректный JSON или обязательные поля заявки.",
                "errors": exc.errors(),
            }),
        )

    @application.post("/lead", response_model=LeadResponse)
    async def create_lead(
        lead: LeadRequest,
        request: Request,
    ) -> LeadResponse | UTF8JSONResponse:
        """Принимает заявку, сохраняет ее и уведомляет менеджера."""
        current_settings: Settings = request.app.state.settings

        try:
            normalized_name = normalize_name(lead.name)
            normalized_contact = normalize_phone(lead.contact)
        except PhoneNormalizationError as exc:
            return UTF8JSONResponse(
                status_code=400,
                content={"detail": str(exc)},
            )

        try:
            init_db(current_settings.database_path)
            stored_lead = save_lead(
                database_path=current_settings.database_path,
                lead=lead,
                normalized_name=normalized_name,
                normalized_contact=normalized_contact,
            )
        except sqlite3.Error as exc:
            write_event(
                current_settings.events_log_path,
                f"Database error while saving lead: {exc}",
            )
            return UTF8JSONResponse(
                status_code=500,
                content={"detail": "База данных временно недоступна."},
            )

        if not stored_lead.created:
            write_event(
                current_settings.events_log_path,
                f"Duplicate lead skipped: {stored_lead.id}.",
            )
            return LeadResponse(
                id=stored_lead.id,
                created=False,
                message="Дубль заявки уже есть в базе.",
            )

        write_event(
            current_settings.events_log_path,
            f"New lead saved: {stored_lead.id}.",
        )

        if current_settings.smtp_configured:
            try:
                send_lead_email(current_settings, lead, stored_lead.id)
                write_event(
                    current_settings.events_log_path,
                    f"Email notification sent for lead: {stored_lead.id}.",
                )
            except EmailNotificationError as exc:
                write_event(
                    current_settings.events_log_path,
                    f"Email notification failed for lead {stored_lead.id}: {exc}",
                )
        else:
            email_skip_message = (
                f"Email notification skipped for lead {stored_lead.id}: "
                "SMTP not configured."
            )
            write_event(
                current_settings.events_log_path,
                email_skip_message,
            )

        return LeadResponse(
            id=stored_lead.id,
            created=True,
            message="Заявка принята и сохранена.",
        )

    return application


app = create_app()
