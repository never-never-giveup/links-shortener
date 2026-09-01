from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.api.deps import to_response
from app.api.schemas import LinkResponse
from app.domain.link import Link
from app.domain.value_objects import ShortCode, TargetUrl


def make_link(
    short_code: str = "abcde1234",
    url: str = "https://example.com",
    clicks: int = 0,
    disabled: bool = False,
    expires_at: datetime | None = None,
    link_id: int = 42,
) -> Link:
    return Link(
        short_code=ShortCode(short_code),
        target_url=TargetUrl(url),
        created_at=datetime(2025, 1, 15, 12, 0, 0, tzinfo=UTC),
        expires_at=expires_at,
        clicks=clicks,
        disabled=disabled,
        id=link_id,
    )


def test_to_response_returns_link_response() -> None:
    link = make_link()
    resp = to_response(link)
    assert isinstance(resp, LinkResponse)
    assert resp.id == 42
    assert resp.short_code == "abcde1234"
    assert resp.target_url == "https://example.com"
    assert resp.clicks == 0
    assert resp.disabled is False
    assert resp.status == "active"


def test_to_response_short_url_format() -> None:
    link = make_link(short_code="myx12345")
    resp = to_response(link)
    assert resp.short_url == "http://127.0.0.1:8000/myx12345"


def test_to_response_disabled_link_status() -> None:
    link = make_link(disabled=True)
    resp = to_response(link)
    assert resp.status == "disabled"


def test_to_response_expired_link_status() -> None:
    link = make_link(expires_at=datetime(2020, 1, 1, tzinfo=UTC))
    resp = to_response(link)
    assert resp.status == "expired"


def test_to_response_without_id_raises() -> None:
    link = Link(
        short_code=ShortCode("abcde1234"),
        target_url=TargetUrl("https://example.com"),
        created_at=datetime.now(UTC),
        id=None,
    )
    with pytest.raises(ValueError, match="unsaved link"):
        to_response(link)


def test_to_response_preserves_expires_at() -> None:
    expires = datetime(2026, 6, 1, tzinfo=UTC)
    link = make_link(expires_at=expires)
    resp = to_response(link)
    assert resp.expires_at == expires


def test_to_response_clicks_preserved() -> None:
    link = make_link(clicks=15)
    resp = to_response(link)
    assert resp.clicks == 15
