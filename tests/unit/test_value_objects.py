from __future__ import annotations

import pytest

from app.domain.errors import InvalidShortCodeError, InvalidUrlError
from app.domain.value_objects import MAX_URL_LENGTH, ShortCode, TargetUrl

MISSING_HOST_URL: str = "http:///path"


def test_short_code_valid_alphanumeric() -> None:
    code = ShortCode("abCd1234")
    assert code.value == "abCd1234"


def test_short_code_min_length() -> None:
    code = ShortCode("abcd")
    assert code.value == "abcd"


def test_short_code_max_length() -> None:
    code = ShortCode("a" * 16)
    assert code.value == "a" * 16


def test_targeturl_valid_https_full() -> None:
    url = TargetUrl("https://example.com/path?query=1#fragment")
    assert url.value == "https://example.com/path?query=1#fragment"


def test_targeturl_valid_http() -> None:
    url = TargetUrl("http://example.com")
    assert url.value == "http://example.com"


def test_targeturl_empty_raises() -> None:
    with pytest.raises(InvalidUrlError, match="empty"):
        TargetUrl("")


def test_targeturl_whitespace_only_raises() -> None:
    with pytest.raises(InvalidUrlError, match="empty"):
        TargetUrl("   ")


def test_targeturl_too_long_raises() -> None:
    too_long = "https://example.com/" + "a" * (MAX_URL_LENGTH - 19)
    with pytest.raises(InvalidUrlError, match=f"longer than {MAX_URL_LENGTH} characters"):
        TargetUrl(too_long)


def test_targeturl_no_scheme_raises() -> None:
    with pytest.raises(InvalidUrlError, match="scheme must be http or https"):
        TargetUrl("example.com")


def test_targeturl_ftp_scheme_raises() -> None:
    with pytest.raises(InvalidUrlError, match="scheme must be http or https"):
        TargetUrl("ftp://example.com")


def test_targeturl_missing_host_raises() -> None:
    with pytest.raises(InvalidUrlError, match="missing host"):
        TargetUrl(MISSING_HOST_URL)


def test_targeturl_credentials_raises() -> None:
    with pytest.raises(InvalidUrlError, match="credentials in URL are not allowed"):
        TargetUrl("https://user:pass@example.com")


def test_targeturl_loopback_localhost_raises() -> None:
    with pytest.raises(InvalidUrlError, match="loopback host is not allowed"):
        TargetUrl("https://localhost/path")


def test_targeturl_loopback_ip6_localhost_raises() -> None:
    with pytest.raises(InvalidUrlError, match="loopback host is not allowed"):
        TargetUrl("https://ip6-localhost/path")


def test_targeturl_loopback_127_0_0_1_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://127.0.0.1/path")


def test_targeturl_private_10_x_ip_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://10.0.0.1/path")


def test_targeturl_private_192_168_ip_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://192.168.1.1/path")


def test_targeturl_private_172_16_ip_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://172.16.0.1/path")


def test_targeturl_link_local_169_254_ip_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://169.254.1.1/path")


def test_targeturl_unspecified_0_0_0_0_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://0.0.0.0/path")


def test_targeturl_multicast_224_ip_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://224.0.0.1/path")


def test_targeturl_reserved_240_ip_raises() -> None:
    with pytest.raises(InvalidUrlError, match="private or reserved IP is not allowed"):
        TargetUrl("https://240.0.0.1/path")


def test_short_code_too_short_raises() -> None:
    with pytest.raises(InvalidShortCodeError, match=r"length must be 4..16"):
        ShortCode("abc")


def test_short_code_too_long_raises() -> None:
    with pytest.raises(InvalidShortCodeError, match=r"length must be 4..16"):
        ShortCode("a" * 17)


def test_short_code_invalid_chars_raises() -> None:
    with pytest.raises(InvalidShortCodeError, match="only ASCII letters and digits are allowed"):
        ShortCode("ab-cd1234")


def test_targeturl_strips_whitespace() -> None:
    url = TargetUrl(" https://example.com ")
    assert url.value == "https://example.com"


def test_targeturl_trailing_dot_hostname_ok() -> None:
    url = TargetUrl("https://example.com./path")
    assert url.value == "https://example.com./path"


def test_targeturl_public_ip_succeeds() -> None:
    url = TargetUrl("https://8.8.8.8/path")
    assert url.value == "https://8.8.8.8/path"


def test_short_code_preserves_value() -> None:
    code = ShortCode("abcDEF123")
    assert code.value == "abcDEF123"


def test_targeturl_preserves_original_form() -> None:
    url = TargetUrl("https://Example.COM/PATH?Q=1")
    assert url.value == "https://Example.COM/PATH?Q=1"
