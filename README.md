# Lead Webhook MVP

Учебный FastAPI-сервис для приема заявок через webhook. Он принимает
`POST /lead`, валидирует контакт, сохраняет заявку в SQLite, пишет событие в
UTF-8 лог и отправляет email-уведомление через SMTP-настройки из `.env`.

## Возможности

- Один endpoint: `POST /lead`.
- SQLite-таблица `leads`.
- Дедупликация по `name.lower()` и телефону, нормализованному в
  `+7XXXXXXXXXX`.
- Лог событий в `events.log`.
- SMTP-уведомление менеджеру через стандартный `smtplib`.
- Понятные HTTP 400 ошибки для некорректного JSON, пустого `contact` и
  неподдерживаемого телефона.
- HTTP 500 и запись в лог при недоступной SQLite-базе.

## Быстрый старт

```powershell
.venv\Scripts\python.exe -m pip install -e .[dev]
Copy-Item .env.example .env
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Сервис будет доступен локально на `http://127.0.0.1:8000`.

## Пример запроса

```powershell
$body = @{
  name = "Ирина"
  contact = "+79990000000"
  source = "landing"
  comment = "Хочу консультацию по тарифам"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/lead" `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
```

Успешный ответ:

```json
{
  "id": 1,
  "created": true,
  "message": "Заявка принята и сохранена."
}
```

Ответ для дубля:

```json
{
  "id": 1,
  "created": false,
  "message": "Дубль заявки уже есть в базе."
}
```

## Настройка `.env`

`.env` не хранится в git. За основу можно взять `.env.example`.

```env
DATABASE_PATH=leads.db
EVENTS_LOG_PATH=events.log
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=manager@example.com
SMTP_PASSWORD=change-me
SMTP_FROM=manager@example.com
SMTP_TO=manager@example.com
SMTP_USE_TLS=true
```

Если SMTP-поля не заполнены, заявка все равно сохраняется, а в `events.log`
появляется запись о пропущенной email-отправке.

## Ручная проверка

Файл `test_payloads.json` содержит 7 примеров payload'ов: успешные заявки,
дубль, пустой `contact` и некорректный телефон.

Для проверки в стиле `curl -s ... | jq` смотри
`docs/manual_requests.md`. В Windows PowerShell лучше вызывать `curl.exe`,
чтобы не попасть в alias PowerShell для `Invoke-WebRequest`. Для кириллицы в
PowerShell используй вариант из документации с UTF-8 файлом и
`--data-binary "@payload.json"`.

## Проверки

```powershell
.venv\Scripts\python.exe -m compileall app tests
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m pytest
```

## OpenSpec

Активная спека находится в
`openspec/changes/001-lead-webhook-mvp/`.
