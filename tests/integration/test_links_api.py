from __future__ import annotations

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
    client: AsyncClient, url: str, custom_code: str | None = None
) -> dict[str, Any]:
    body: dict[str, Any] = {"url": url}
    if custom_code is not None:
        body["custom_code"] = custom_code
    resp = await client.post("/links", json=body)
    assert resp.status_code == 201
    return resp.json()


async def test_post_link_returns_201() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.post("/links", json={"url": "https://example.com"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["short_code"]
        assert body["target_url"] == "https://example.com"
        assert body["clicks"] == 0
        assert body["disabled"] is False
        assert body["status"] == "active"


async def test_post_link_with_custom_code() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.post(
            "/links",
            json={"url": "https://example.com", "custom_code": "mycode1234"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["short_code"] == "mycode1234"


async def test_post_link_empty_url_returns_422() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.post("/links", json={"url": ""})
        assert resp.status_code == 422


async def test_post_link_invalid_url_returns_422() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.post("/links", json={"url": "not-a-url"})
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body


async def test_post_link_saves_to_db() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        await client.post("/links", json={"url": "https://example.com"})
        async with SessionLocal() as session:
            rows = (await session.execute(text("SELECT * FROM links"))).fetchall()
            assert len(rows) == 1
            assert rows[0].target_url == "https://example.com"


async def test_post_link_duplicate_custom_code_returns_409() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        await client.post("/links", json={"url": "https://example.com", "custom_code": "dup1234"})
        resp = await client.post(
            "/links",
            json={"url": "https://other.com", "custom_code": "dup1234"},
        )
        assert resp.status_code == 409


async def test_get_link_by_code_returns_200() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        resp = await client.get(f"/links/{link['short_code']}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["target_url"] == "https://example.com"
        assert body["short_code"] == link["short_code"]


async def test_get_link_nonexistent_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.get("/links/nonexistent")
        assert resp.status_code == 404


async def test_list_links_returns_list() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        await _create_link(client, "https://example.com")
        await _create_link(client, "https://other.com")
        resp = await client.get("/links")
        assert resp.status_code == 200
        body: list[dict[str, Any]] = resp.json()
        assert isinstance(body, list)
        assert len(body) == 2


async def test_list_links_empty_returns_empty_list() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.get("/links")
        assert resp.status_code == 200
        body = resp.json()
        assert body == []


async def test_disable_link_returns_200() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        resp = await client.post(f"/links/{link['short_code']}/disable")
        assert resp.status_code == 200
        body = resp.json()
        assert body["disabled"] is True


async def test_disable_link_nonexistent_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.post("/links/nonexistent/disable")
        assert resp.status_code == 404


async def test_post_link_with_ttl_returns_expires() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.post("/links", json={"url": "https://example.com", "ttl_seconds": 3600})
        assert resp.status_code == 201
        body = resp.json()
        assert body["expires_at"] is not None


async def test_disable_link_updates_db() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        await client.post(f"/links/{link['short_code']}/disable")
        async with SessionLocal() as session:
            rows = (await session.execute(text("SELECT * FROM links"))).fetchall()
            assert rows[0].disabled is True


async def test_delete_link_returns_204() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        resp = await client.delete(f"/links/{link['short_code']}")
        assert resp.status_code == 204
        assert resp.content == b""
        # После удаления ссылка недоступна
        assert (await client.get(f"/links/{link['short_code']}")).status_code == 404


async def test_delete_link_nonexistent_returns_404() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        resp = await client.delete("/links/nonexistent")
        assert resp.status_code == 404


async def test_delete_link_removes_from_db() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=False
    ) as client:
        link = await _create_link(client, "https://example.com")
        await client.delete(f"/links/{link['short_code']}")
        async with SessionLocal() as session:
            rows = (await session.execute(text("SELECT * FROM links"))).fetchall()
            assert rows == []
