from __future__ import annotations

import pytest

from app.domain.errors import (
    DomainError,
    InvalidShortCodeError,
    InvalidUrlError,
    LinkDisabledError,
    LinkExpiredError,
    LinkNotFoundError,
    ShortCodeTakenError,
)


def test_domain_error_is_exception() -> None:
    err = DomainError()
    assert isinstance(err, Exception)


def test_domain_error_default_message() -> None:
    err = DomainError()
    assert str(err) == ""


def test_invalid_url_error_message() -> None:
    err = InvalidUrlError("empty")
    assert str(err) == "Invalid target URL: empty"
    assert err.reason == "empty"


def test_invalid_short_code_error_message() -> None:
    err = InvalidShortCodeError("too short")
    assert str(err) == "Invalid short code: too short"
    assert err.reason == "too short"


def test_short_code_taken_error_message() -> None:
    err = ShortCodeTakenError("mycode123")
    assert str(err) == "Short code already taken: mycode123"
    assert err.short_code == "mycode123"


def test_link_not_found_error_message() -> None:
    err = LinkNotFoundError("code1234")
    assert str(err) == "Link not found: code1234"
    assert err.short_code == "code1234"


def test_link_expired_error_message() -> None:
    err = LinkExpiredError("expired1234")
    assert str(err) == "Link expired: expired1234"
    assert err.short_code == "expired1234"


def test_link_disabled_error_message() -> None:
    err = LinkDisabledError("disabled1234")
    assert str(err) == "Link disabled: disabled1234"
    assert err.short_code == "disabled1234"


def test_all_domain_errors_inherit_from_domain_error() -> None:
    assert issubclass(InvalidUrlError, DomainError)
    assert issubclass(InvalidShortCodeError, DomainError)
    assert issubclass(ShortCodeTakenError, DomainError)
    assert issubclass(LinkNotFoundError, DomainError)
    assert issubclass(LinkExpiredError, DomainError)
    assert issubclass(LinkDisabledError, DomainError)


def test_domain_errors_are_exceptions() -> None:
    for err_cls in [
        InvalidUrlError,
        InvalidShortCodeError,
        ShortCodeTakenError,
        LinkNotFoundError,
        LinkExpiredError,
        LinkDisabledError,
    ]:
        with pytest.raises(err_cls):
            raise err_cls("test")
