from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.domain.link import Link, LinkStatus
from app.domain.value_objects import ShortCode, TargetUrl


def make_link(
    short_code: str = "abcde1234",
    url: str = "https://example.com",
    disabled: bool = False,
    expires_at: datetime | None = None,
    clicks: int = 0,
) -> Link:
    return Link(
        short_code=ShortCode(short_code),
        target_url=TargetUrl(url),
        created_at=datetime.now(UTC),
        expires_at=expires_at,
        clicks=clicks,
        disabled=disabled,
        id=1,
    )


def test_link_status_active_by_default() -> None:
    link = make_link()
    assert link.status(datetime.now(UTC)) is LinkStatus.ACTIVE


def test_link_status_disabled() -> None:
    link = make_link(disabled=True)
    assert link.status(datetime.now(UTC)) is LinkStatus.DISABLED


def test_link_status_expired() -> None:
    link = make_link(expires_at=datetime.now(UTC) - timedelta(seconds=60))
    assert link.status(datetime.now(UTC)) is LinkStatus.EXPIRED


def test_link_status_expired_disabled_returns_disabled() -> None:
    link = make_link(disabled=True, expires_at=datetime.now(UTC) - timedelta(seconds=60))
    assert link.status(datetime.now(UTC)) is LinkStatus.DISABLED


def test_link_status_not_expired_yet() -> None:
    link = make_link(expires_at=datetime.now(UTC) + timedelta(seconds=3600))
    assert link.status(datetime.now(UTC)) is LinkStatus.ACTIVE


def test_link_is_active_returns_true() -> None:
    link = make_link()
    assert link.is_active(datetime.now(UTC)) is True


def test_link_is_active_expired_returns_false() -> None:
    link = make_link(expires_at=datetime.now(UTC) - timedelta(seconds=60))
    assert link.is_active(datetime.now(UTC)) is False


def test_link_is_active_disabled_returns_false() -> None:
    link = make_link(disabled=True)
    assert link.is_active(datetime.now(UTC)) is False


def test_link_with_click_increments_clicks() -> None:
    link = make_link(clicks=5)
    result = link.with_click()
    assert result.clicks == 6
    assert link.clicks == 5


def test_link_disable_returns_disabled_copy() -> None:
    link = make_link()
    result = link.disable()
    assert result.disabled is True
    assert link.disabled is False


def test_link_frozen_attributes_preserved() -> None:
    link = make_link()
    assert link.id == 1
    assert link.short_code.value == "abcde1234"
    assert link.target_url.value == "https://example.com"
