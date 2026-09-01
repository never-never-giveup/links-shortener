from __future__ import annotations

import pytest
from fastapi import HTTPException, status

from app.api.errors import raise_for_domain_error
from app.domain.errors import (
    DomainError,
    InvalidShortCodeError,
    InvalidUrlError,
    LinkDisabledError,
    LinkExpiredError,
    LinkNotFoundError,
    ShortCodeTakenError,
)


def test_raise_for_invalid_url_error_returns_422() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(InvalidUrlError("empty"))
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "empty" in exc_info.value.detail


def test_raise_for_invalid_short_code_error_returns_422() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(InvalidShortCodeError("too short"))
    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_raise_for_short_code_taken_error_returns_409() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(ShortCodeTakenError("mycode123"))
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "mycode123" in exc_info.value.detail


def test_raise_for_link_not_found_error_returns_404() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(LinkNotFoundError("code1234"))
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "code1234" in exc_info.value.detail


def test_raise_for_link_expired_error_returns_410() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(LinkExpiredError("expired1234"))
    assert exc_info.value.status_code == status.HTTP_410_GONE
    assert "expired1234" in exc_info.value.detail


def test_raise_for_link_disabled_error_returns_404() -> None:
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(LinkDisabledError("disabled1234"))
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_raise_for_unknown_domain_error_returns_500() -> None:
    class UnknownDomainError(DomainError):
        pass

    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(UnknownDomainError())
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_raise_for_domain_error_preserves_cause() -> None:
    original = LinkNotFoundError("code1234")
    with pytest.raises(HTTPException) as exc_info:
        raise_for_domain_error(original)
    assert exc_info.value.__cause__ is original
