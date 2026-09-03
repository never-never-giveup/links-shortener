# External source: Alembic

- **URL:** https://alembic.sqlalchemy.org/
- **Дата проверки:** 2026-09-03
- **Тип:** документация инструмента миграций

## Что берёт вики

Миграции схемы БД выполняются через Alembic. Зависимость зафиксирована во
внутреннем первоисточнике `pyproject.toml`: `alembic>=1.14.0`. Используемые
механизмы Alembic, подтверждённые кодом:

- Конфигурация `alembic.ini` (`script_location = alembic`, `prepend_sys_path = .`).
- Асинхронный прогон миграций через `async_engine_from_config(..., poolclass=NullPool)`
  и `asyncio.run(...)` — `alembic/env.py:29-44`, функции `run_async_migrations` и
  `run_migrations_online`.
- `target_metadata = Base.metadata` — `alembic/env.py:20`.
- Регистрация моделей: `from app.db import models` — `alembic/env.py:11`.

## Факты, подтверждённые внешним источником

- `NullPool` отключает пулинг соединений при прогоне миграций (одноразовое
  подключение, нет удержания коннектов между операциями DDL).
- `down_revision` связывает миграции в цепочку; у первой миграции `down_revision = None`.
