from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text

from app.db.session import get_sessionmaker

SessionLocal = get_sessionmaker()


@pytest.fixture(autouse=True)
async def clean_db() -> AsyncGenerator[None]:
    """Очищает таблицу links до и после каждого теста."""
    async with SessionLocal() as session:
        await session.execute(text("DELETE FROM links"))
        await session.commit()
    yield
    async with SessionLocal() as session:
        await session.execute(text("DELETE FROM links"))
        await session.commit()
