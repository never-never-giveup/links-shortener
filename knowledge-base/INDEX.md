# INDEX — карта базы знаний

База знаний по репозиторию FastAPI-трека (сокращатель ссылок). Метод — LLM Wiki
(заземлённые факты, связанные страницы, пробелы вместо догадок). Правила и
операции — [AGENTS.md](AGENTS.md).

## Точка входа

| Файл | Назначение |
|---|---|
| [AGENTS.md](AGENTS.md) | Схема вики и правила операций: ingest, query, lint, filing back |
| [LOG.md](LOG.md) | Append-only журнал событий базы знаний |

## Слой `raw/` — внешние первоисточники

| Карточка | Источник | Дата проверки |
|---|---|---|
| [raw/README.md](raw/README.md) | Описание слоя и реестр карточек | — |
| [raw/conventional-commits.md](raw/conventional-commits.md) | conventionalcommits.org | 2026-09-03 |
| [raw/keep-a-changelog.md](raw/keep-a-changelog.md) | keepachangelog.com | 2026-09-03 |
| [raw/fastapi.md](raw/fastapi.md) | fastapi.tiangolo.com | 2026-09-03 |
| [raw/sqlalchemy.md](raw/sqlalchemy.md) | docs.sqlalchemy.org | 2026-09-03 |
| [raw/alembic.md](raw/alembic.md) | alembic.sqlalchemy.org | 2026-09-03 |

## Слой `wiki/` — связанные страницы

| Страница | Краткое описание |
|---|---|
| [wiki/overview.md](wiki/overview.md) | Верхний обзор: что это, стек, возможности, качество, пробелы |
| [wiki/architecture.md](wiki/architecture.md) | Слои приложения, поток запроса `POST /links` и `GET /{short_code}`, конфигурация запуска |
| [wiki/decisions.md](wiki/decisions.md) | Зафиксированные решения D1–D8 и пробелы G1–G8 |
| [wiki/domain/links.md](wiki/domain/links.md) | Доменные сущности и value objects: `Link`, `TargetUrl`, `ShortCode`, SSRF-фильтр, ошибки |
| [wiki/contracts/http-api.md](wiki/contracts/http-api.md) | HTTP-контракт: эндпоинты, DTO `LinkResponse`, маппинг ошибок в HTTP |
| [wiki/contracts/database.md](wiki/contracts/database.md) | Схема БД, таблица `links`, маппинг ORM↔домен, репозиторий, сессии |
| [wiki/testing/strategy.md](wiki/testing/strategy.md) | Подход к тестам: 113 тестов, 100% coverage, Fake-репозиторий, locust |
| [wiki/runbooks/local-development.md](wiki/runbooks/local-development.md) | Запуск локально: БД, .env, миграции, проверки, pre-commit |

## Как пользоваться

1. Начни с [AGENTS.md](AGENTS.md) (правила) и этой карты.
2. Открой нужную страницу `wiki/`.
3. Каждый нетривиальный факт заземлён: внутренний — `file:line` + имя, внешний —
   карточка `raw/` (URL + дата).
4. Неизвестное помечено как пробел (`G<N>` в [wiki/decisions.md](wiki/decisions.md)).
