from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import (
    InvalidUrlError,
    LinkDisabledError,
    LinkExpiredError,
    LinkNotFoundError,
    ShortCodeTakenError,
)
from app.domain.link import Link
from app.domain.value_objects import ShortCode, TargetUrl
from app.services.link_service import LinkService


class FakeLinkRepository:
    """In-memory репозиторий с async-сигнатурами как у LinkRepositoryProtocol."""

    def __init__(self) -> None:
        self._store: dict[str, Link] = {}
        self._next_id: int = 1

    async def add(self, link: Link) -> Link:
        stored = replace(link, id=self._next_id)
        self._store[link.short_code.value] = stored
        self._next_id += 1
        return stored

    async def get_by_code(self, short_code: str) -> Link | None:
        return self._store.get(short_code)

    async def list_all(self, limit: int = 100) -> list[Link]:
        items = list(self._store.values())
        return items[:limit]

    async def update(self, link: Link) -> Link:
        self._store[link.short_code.value] = link
        return link

    async def delete_by_code(self, short_code: str) -> bool:
        if short_code in self._store:
            del self._store[short_code]
            return True
        return False


def make_service() -> tuple[LinkService, FakeLinkRepository]:
    """Создаёт сервис с in-memory Fake-репозиторием."""
    repo = FakeLinkRepository()
    return LinkService(repo), repo


# --- create_link ---


async def test_create_link_with_generated_code_returns_link() -> None:
    service, _ = make_service()
    link = await service.create_link("https://example.com")
    assert link.id is not None
    assert len(link.short_code.value) == 7
    assert link.target_url.value == "https://example.com"
    assert link.clicks == 0
    assert link.disabled is False
    assert link.expires_at is None


async def test_create_link_with_custom_code_returns_link() -> None:
    service, _ = make_service()
    link = await service.create_link("https://example.com", custom_code="mycode123")
    assert link.short_code.value == "mycode123"


async def test_create_link_with_taken_custom_code_raises() -> None:
    service, _ = make_service()
    await service.create_link("https://example.com", custom_code="mycode123")
    with pytest.raises(ShortCodeTakenError, match="mycode123"):
        await service.create_link("https://other.com", custom_code="mycode123")


async def test_create_link_with_ttl_sets_expires_at() -> None:
    service, _ = make_service()
    link = await service.create_link("https://example.com", ttl_seconds=60)
    assert link.expires_at is not None
    assert link.expires_at > datetime.now(UTC)


async def test_create_link_with_zero_ttl_has_no_expiry() -> None:
    service, _ = make_service()
    link = await service.create_link("https://example.com", ttl_seconds=0)
    assert link.expires_at is None


async def test_create_link_with_negative_ttl_has_no_expiry() -> None:
    service, _ = make_service()
    link = await service.create_link("https://example.com", ttl_seconds=-10)
    assert link.expires_at is None


async def test_create_link_with_invalid_url_raises() -> None:
    service, _ = make_service()
    with pytest.raises(InvalidUrlError, match="scheme must be http or https"):
        await service.create_link("not-a-url")


# --- get_link ---


async def test_get_link_returns_existing_link() -> None:
    service, _ = make_service()
    created = await service.create_link("https://example.com")
    link = await service.get_link(created.short_code.value)
    assert link.short_code.value == created.short_code.value


async def test_get_link_nonexistent_raises() -> None:
    service, _ = make_service()
    with pytest.raises(LinkNotFoundError, match="code1234"):
        await service.get_link("code1234")


# --- list_links ---


async def test_list_links_returns_all_links() -> None:
    service, _ = make_service()
    await service.create_link("https://example.com")
    await service.create_link("https://other.com")
    links = await service.list_links()
    assert len(links) == 2


async def test_list_links_empty_returns_empty_list() -> None:
    service, _ = make_service()
    links = await service.list_links()
    assert links == []


async def test_list_links_respects_limit() -> None:
    service, _ = make_service()
    for _ in range(5):
        await service.create_link("https://example.com")
    links = await service.list_links(limit=3)
    assert len(links) == 3


# --- resolve ---


async def test_resolve_active_link_increments_clicks() -> None:
    service, _ = make_service()
    created = await service.create_link("https://example.com")
    resolved = await service.resolve(created.short_code.value)
    assert resolved.clicks == 1
    assert resolved.short_code.value == created.short_code.value


async def test_resolve_expired_link_raises() -> None:
    service, repo = make_service()
    await repo.add(
        Link(
            short_code=ShortCode("expired1234"),
            target_url=TargetUrl("https://example.com"),
            created_at=datetime.now(UTC) - timedelta(seconds=120),
            expires_at=datetime.now(UTC) - timedelta(seconds=60),
        )
    )
    with pytest.raises(LinkExpiredError, match="expired1234"):
        await service.resolve("expired1234")


async def test_resolve_disabled_link_raises() -> None:
    service, repo = make_service()
    await repo.add(
        Link(
            short_code=ShortCode("disabled1234"),
            target_url=TargetUrl("https://example.com"),
            created_at=datetime.now(UTC),
            disabled=True,
        )
    )
    with pytest.raises(LinkDisabledError, match="disabled1234"):
        await service.resolve("disabled1234")


# --- disable_link ---


async def test_disable_link_returns_disabled_link() -> None:
    service, _ = make_service()
    created = await service.create_link("https://example.com")
    disabled = await service.disable_link(created.short_code.value)
    assert disabled.disabled is True
    assert disabled.short_code.value == created.short_code.value


async def test_disable_link_nonexistent_raises() -> None:
    service, _ = make_service()
    with pytest.raises(LinkNotFoundError, match="code1234"):
        await service.disable_link("code1234")


# --- delete_link ---


async def test_delete_link_removes_link() -> None:
    service, repo = make_service()
    created = await service.create_link("https://example.com")
    await service.delete_link(created.short_code.value)
    assert await repo.get_by_code(created.short_code.value) is None


async def test_delete_link_nonexistent_raises() -> None:
    service, _ = make_service()
    with pytest.raises(LinkNotFoundError, match="code1234"):
        await service.delete_link("code1234")
