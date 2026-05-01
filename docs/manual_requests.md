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
для `Invoke-WebRequest`. JSON удобнее передавать через переменную: так
PowerShell не ломает кавычки внутри тела запроса.

Для корректного вывода кириллицы в Windows PowerShell 5.x перед запросами
можно переключить консоль на UTF-8:

```powershell
chcp 65001
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
```

Надежный вариант для `curl.exe`: записать тело запроса во временный UTF-8 файл
без BOM и передать его через `--data-binary`. Так PowerShell не заменит
кириллицу на `?` при передаче аргумента внешней программе.

```powershell
$body = @{
  name = "Ирина"
  contact = "+79990000000"
  source = "landing"
  comment = "Хочу консультацию по тарифам"
} | ConvertTo-Json -Compress

$payloadPath = Join-Path $env:TEMP "lead-payload.json"
[System.IO.File]::WriteAllText(
  $payloadPath,
  $body,
  [System.Text.UTF8Encoding]::new($false)
)

curl.exe -s -X POST "http://localhost:8000/lead" `
  -H "Content-Type: application/json; charset=utf-8" `
  --data-binary "@$payloadPath" | jq
```

Если `jq` не установлен, временно уберите `| jq`: API все равно вернет JSON.

Для PowerShell-native запроса:

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

## Если в SQLite уже попали `?????`

Такие строки нельзя восстановить автоматически: исходная кириллица была
заменена на `?` до попадания запроса на сервер. Для учебного локального запуска
можно остановить `uvicorn`, удалить `leads.db` и отправить запрос заново через
UTF-8-safe команду выше.

Проверить реальные байты в базе можно так:

```powershell
@'
import sqlite3

with sqlite3.connect("leads.db") as connection:
    rows = connection.execute(
        "SELECT id, name, hex(name), comment, hex(comment) FROM leads"
    ).fetchall()
    for row in rows:
        print(row)
'@ | .venv\Scripts\python.exe -
```
