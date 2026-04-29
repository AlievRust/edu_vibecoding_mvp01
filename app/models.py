"""Pydantic-схемы входящих заявок и ответов API."""

from pydantic import BaseModel, Field, field_validator


class LeadRequest(BaseModel):
    """Входящий JSON для endpoint `POST /lead`."""

    name: str = Field(default="Без имени", description="Имя клиента.")
    contact: str = Field(..., description="Телефон клиента для связи.")
    source: str = Field(default="unknown", description="Источник заявки.")
    comment: str = Field(default="", description="Комментарий клиента.")

    @field_validator("name", "source", "comment", mode="before")
    @classmethod
    def strip_optional_text(cls, value: object) -> str:
        """Приводит необязательные текстовые поля к аккуратной строке."""
        if value is None:
            return ""
        return str(value).strip()

    @field_validator("contact", mode="before")
    @classmethod
    def require_contact(cls, value: object) -> str:
        """Запрещает пустой контакт, чтобы заявка не терялась."""
        if value is None or not str(value).strip():
            raise ValueError("Поле contact обязательно для заявки.")
        return str(value).strip()


class LeadResponse(BaseModel):
    """Ответ API после обработки заявки."""

    id: int
    created: bool
    message: str
