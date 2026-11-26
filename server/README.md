# Очередь обращений (Ticket Queue)

## Запуск
Одной командой:
```bash
docker compose up --build -d
```

SWAGGER доступен по адресу - http://localhost:8000/docs

## Локальный запуск

1) Установите зависимости: `pip install -r requirements.txt`

2) Запустите Postgres и Redis (например, через `docker compose up db redis`)

3) Примените миграции: `alembic upgrade head`

4) Запустите API: `uvicorn app.main:app --reload`

5) Запустите воркер: `arq app.worker.WorkerSettings`

## Тесты

`pytest -q`

## Архитектура и решения
Стек: FastAPI, SQLAlchemy (async), PostgreSQL, ARQ (Redis), Alembic.

База данных: Выбрана PostgreSQL. В модели создан составной индекс (status, created_at DESC) для оптимизации запроса списка с фильтром.

Очередь и идемпотентность: Используется ARQ. В воркере реализована блокировка строки FOR UPDATE, чтобы исключить гонки данных. Повторный запуск джоба проверяет статус (если processing/done/failed — пропускает).

Ретраи: Настроены в ARQ (max_tries=3). При ошибке статус переводится в failed с записью причины в БД и лог.

Обработка ошибок: Недопустимые переходы статусов возвращают 409 (через доменное исключение InvalidTransition). Ошибки валидации — 422 (Pydantic).