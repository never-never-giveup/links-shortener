from __future__ import annotations

import asyncio
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db.session import get_sessionmaker
from app.main import app

SessionLocal = get_sessionmaker()


@pytest.fixture(autouse=True)
async def clean_db() -> None:
    async with SessionLocal() as session:
        await session.execute(text("DELETE FROM links"))
        await session.commit()


async def _create_link(
    client: AsyncClient, url: str, custom_code: str | None = None, ttl: int | None = None
) -> dict[str, Any]:
    body: dict[str, Any] = {"url": url}
    if custom_code is not None:
        body["custom_code"] = custom_code
    if ttl is not None:
        body["ttl_seconds"] = ttl
    resp = await client.post("/links", json=body)
    assert resp.status_code == 201
    return resp.json()


async def test_redirect_active_link_returns_307() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        resp = await client.get(f"/{link['short_code']}")
        assert resp.status_code == 307
        assert resp.headers["location"] == "https://example.com"


async def test_redirect_increments_clicks() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        await client.get(f"/{link['short_code']}")
        await client.get(f"/{link['short_code']}")
        async with SessionLocal() as session:
            row = (
                await session.execute(
                    text(f"SELECT clicks FROM links WHERE short_code = '{link['short_code']}'")
                )
            ).fetchone()
        assert row is not None
        assert row.clicks == 2


async def test_redirect_nonexistent_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.get("/nonexistent")
        assert resp.status_code == 404


async def test_redirect_expired_link_returns_410() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com", ttl=1)
        await asyncio.sleep(2)
        resp = await client.get(f"/{link['short_code']}")
        assert resp.status_code == 410


async def test_redirect_disabled_link_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        await client.post(f"/links/{link['short_code']}/disable")
        resp = await client.get(f"/{link['short_code']}")
        assert resp.status_code == 404


async def test_redirect_404_for_nonexistent_code() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.get("/notalinkprefix")
        assert resp.status_code == 404
