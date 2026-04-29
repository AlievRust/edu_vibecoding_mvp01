# Ручные запросы через curl и jq

Эти команды проверяют реальный endpoint проекта: `POST /lead`.
Сервис должен быть запущен локально:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Bash, Git Bash, WSL

Успешная новая заявка:

```bash
curl -s -X POST http://localhost:8000/lead \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Ирина",
    "contact": "+79990000000",
    "source": "landing",
    "comment": "Хочу консультацию по тарифам"
  }' | jq
```

Проверка дубля по имени и нормализованному телефону:

```bash
curl -s -X POST http://localhost:8000/lead \
  -H 'Content-Type: application/json' \
  -d '{
    "name": " ирина ",
    "contact": "8 (999) 000-00-00",
    "source": "social",
    "comment": "Повторная заявка"
  }' | jq
```

Пустой `contact`, ожидается HTTP 400:

```bash
curl -s -X POST http://localhost:8000/lead \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Павел",
    "contact": "",
    "source": "landing",
    "comment": "Некорректный payload"
  }' | jq
```

Некорректный телефон, ожидается HTTP 400:

```bash
curl -s -X POST http://localhost:8000/lead \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Сергей",
    "contact": "+123",
    "source": "landing",
    "comment": "Не российский номер"
  }' | jq
```

## Windows PowerShell

В Windows PowerShell используйте `curl.exe`, потому что `curl` может быть alias
для `Invoke-WebRequest`.

```powershell
curl.exe -s -X POST http://localhost:8000/lead `
  -H 'Content-Type: application/json' `
  -d '{
    "name": "Ирина",
    "contact": "+79990000000",
    "source": "landing",
    "comment": "Хочу консультацию по тарифам"
  }' | jq
```

Если `jq` не установлен, временно уберите `| jq`: API все равно вернет JSON.
