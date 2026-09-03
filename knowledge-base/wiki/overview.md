# Overview

> Страница вики. Уровень: верхний обзор. Источник фактов — код репозитория FastAPI-трека.

## Что это

Бэкенд-сервис **сокращателя ссылок** (link shortener) на FastAPI. Создаёт короткие
коды для произвольных URL, редиректит по короткому коду, считает переходы, поддерживает
TTL (срок жизни) и ручное отключение ссылок.

- Идентичность проекта: `pyproject.toml` — `name = "ai-python-workshop"`,
  `description = "AI-first Python workshop — FastAPI track (link shortener)"`.
- Требование к Python: `requires-python = ">=3.14"` — `pyproject.toml`.

## Технологический стек

| Компонент | Версия (нижняя граница) | Где зафиксировано |
|---|---|---|
| FastAPI | `>=0.137.0` | `pyproject.toml`, зависимости |
| SQLAlchemy (async) | `>=2.0.36` | `pyproject.toml`, зависимости |
| psycopg (binary) | `>=3.2.0` | `pyproject.toml`, зависимости |
| Alembic | `>=1.14.0` | `pyproject.toml`, зависимости |
| pydantic-settings | `>=2.6.0` | `pyproject.toml`, зависимости |
| structlog | `>=24.4.0` | `pyproject.toml`, зависимости |

Дев-зависимости (pytest, ruff, basedpyright, bandit, pip-audit, locust, httpx,
aiosqlite) — `pyproject.toml`, секция `[dependency-groups] dev`.

> Внешние первоисточники по фреймворкам — см. [../raw/fastapi.md](../raw/fastapi.md),
> [../raw/sqlalchemy.md](../raw/sqlalchemy.md), [../raw/alembic.md](../raw/alembic.md).

## Основные возможности (по маршрутам)

| Возможность | Маршрут | Файл:функция |
|---|---|---|
| Создать короткую ссылку | `POST /links` | `app/api/routes.py:13` `create_link` |
| Получить ссылку по коду | `GET /links/{short_code}` | `app/api/routes.py:30` `get_link` |
| Список ссылок | `GET /links` | `app/api/routes.py:24` `list_links` |
| Отключить ссылку | `POST /links/{short_code}/disable` | `app/api/routes.py:39` `disable_link` |
| Удалить ссылку | `DELETE /links/{short_code}` | `app/api/routes.py:48` `delete_link` |
| Редирект по короткому коду | `GET /{short_code}` | `app/main.py:12` `redirect_to_target` |

Подробно контракты — на странице [contracts/http-api.md](contracts/http-api.md).

## База данных

PostgreSQL. Контейнер `postgres:17` поднимается через `docker-compose.yml`.
Схема — одна таблица `links`. Детально — [contracts/database.md](contracts/database.md).

## Качество и проверки

- Линтер: ruff (`pyproject.toml`, `[tool.ruff]`, target `py314`, line-length 100).
- Тайп-чекер: basedpyright в strict-режиме (`pyproject.toml`, `[tool.basedpyright]`).
- Тесты: pytest, asyncio mode auto, 113 тестов (см. [testing/strategy.md](testing/strategy.md)).
- Coverage-гейт: `fail_under = 100` — `pyproject.toml`, `[tool.coverage.report]`.
- pre-commit: ruff, basedpyright, bandit, pip-audit, gitleaks, uv-lock-check —
  `.pre-commit-config.yaml`.

## Дальнейшее чтение

- [architecture.md](architecture.md) — слои и поток запроса.
- [domain/links.md](domain/links.md) — доменные правила и инварианты.
- [decisions.md](decisions.md) — зафиксированные решения и пробелы.

## Пробелы

- В корне репозитория **нет `README.md`** (правила `.agents/agents/docs.md` требуют
  разделы Overview/Quickstart/Configuration/Running/Architecture/API). См. [decisions.md](decisions.md).
- В корне репозитория **нет `CHANGELOG.md`** (правила `.agents/agents/docs.md`
  предписывают Keep a Changelog). См. [decisions.md](decisions.md).
- **Нет CI-конфигурации** для FastAPI-приложения: файл `.gitlab-ci.yml` существует
  только в `.agents/` и относится к документационному репозиторию правил, не к
  приложению. См. [decisions.md](decisions.md).
