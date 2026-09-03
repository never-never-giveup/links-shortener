# External source: SQLAlchemy

- **URL:** https://docs.sqlalchemy.org/
- **Дата проверки:** 2026-09-03
- **Тип:** документация ORM/движка БД

## Что берёт вики

Проект использует SQLAlchemy 2.0 async. Зависимость зафиксирована во внутреннем
первоисточнике `pyproject.toml`: `sqlalchemy[asyncio]>=2.0.36`. Используемые
механизмы SQLAlchemy, подтверждённые кодом:

- `DeclarativeBase` — `app/db/base.py:6`, класс `Base`.
- `Mapped[...]` + `mapped_column(...)` — `app/db/models.py:11-22`, класс `LinkModel`.
- `create_async_engine(..., pool_size=..., max_overflow=..., pool_pre_ping=True)` —
  `app/db/session.py:21-26`, функция `get_engine`.
- `async_sessionmaker(..., expire_on_commit=False)` — `app/db/session.py:30-31`,
  функция `get_sessionmaker`.
- `select`/`update`/`delete` конструкции — `app/repositories/link_repository.py:47,58,68`.
- Транзакционный контекст сессии (commit/rollback) — `app/db/session.py:34-42`,
  функция `provide_session`.

## Факты, подтверждённые внешним источником

- `pool_pre_ping=True` включает проверку живости соединения перед выдачей из пула
  (защита от stale-коннектов).
- `expire_on_commit=False` сохраняет атрибуты объектов доступными после commit.
