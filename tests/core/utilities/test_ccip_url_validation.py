import pytest
import socket

from web3.exceptions import (
    Web3ValidationError,
)
from web3.utils.ccip_url_validation import (
    validate_ccip_url_host,
    validate_ccip_url_scheme,
)

# -- validate_ccip_url_scheme tests -- #


class TestValidateCcipUrlScheme:
    def test_https_passes(self):
        validate_ccip_url_scheme("https://example.com/api", allow_http=False)

    def test_http_fails_by_default(self):
        with pytest.raises(Web3ValidationError, match="non-HTTPS"):
            validate_ccip_url_scheme("http://example.com/api")

    def test_http_passes_with_allow_http(self):
        validate_ccip_url_scheme("http://example.com/api", allow_http=True)

    def test_ftp_always_fails(self):
        with pytest.raises(Web3ValidationError, match="not allowed"):
            validate_ccip_url_scheme("ftp://example.com/file")

    def test_ftp_fails_even_with_allow_http(self):
        with pytest.raises(Web3ValidationError, match="not allowed"):
            validate_ccip_url_scheme("ftp://example.com/file", allow_http=True)

    def test_file_scheme_fails(self):
        with pytest.raises(Web3ValidationError, match="not allowed"):
            validate_ccip_url_scheme("file:///etc/passwd")

    def test_file_scheme_fails_with_allow_http(self):
        with pytest.raises(Web3ValidationError, match="not allowed"):
            validate_ccip_url_scheme("file:///etc/passwd", allow_http=True)


# -- validate_ccip_url_host tests -- #


class TestValidateCcipUrlHost:
    def _patch_getaddrinfo(self, monkeypatch, ip):
        def _mock_getaddrinfo(host, port, *args, **kwargs):
            return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", (ip, 0))]

        monkeypatch.setattr("socket.getaddrinfo", _mock_getaddrinfo)

    def test_public_ip_passes(self, monkeypatch):
        self._patch_getaddrinfo(monkeypatch, "8.8.8.8")
        validate_ccip_url_host("https://example.com/api")

    @pytest.mark.parametrize(
        "blocked_ip",
        [
            "127.0.0.1",
            "127.0.0.2",
            "10.0.0.1",
            "10.255.255.255",
            "172.16.0.1",
            "172.31.255.255",
            "192.168.0.1",
            "192.168.1.100",
            "169.254.0.1",
            "0.0.0.0",
        ],
    )
    def test_blocked_ipv4(self, monkeypatch, blocked_ip):
        self._patch_getaddrinfo(monkeypatch, blocked_ip)
        with pytest.raises(Web3ValidationError, match="blocked private/reserved"):
            validate_ccip_url_host("https://example.com/api")

    def test_blocked_ipv6_loopback(self, monkeypatch):
        def _mock_getaddrinfo(host, port, *args, **kwargs):
            return [(socket.AF_INET6, socket.SOCK_STREAM, 0, "", ("::1", 0, 0, 0))]

        monkeypatch.setattr("socket.getaddrinfo", _mock_getaddrinfo)
        with pytest.raises(Web3ValidationError, match="blocked private/reserved"):
            validate_ccip_url_host("https://example.com/api")

    def test_unresolvable_hostname(self, monkeypatch):
        def _mock_getaddrinfo(host, port, *args, **kwargs):
            raise socket.gaierror("Name or service not known")

        monkeypatch.setattr("socket.getaddrinfo", _mock_getaddrinfo)
        with pytest.raises(Web3ValidationError, match="could not be resolved"):
            validate_ccip_url_host("https://nonexistent.invalid/api")

    def test_no_hostname(self):
        with pytest.raises(Web3ValidationError, match="no hostname"):
            validate_ccip_url_host("https:///path")


# -- custom validator tests -- #


class TestCustomUrlValidator:
    def test_custom_validator_called_and_can_reject(self):
        calls = []

        def reject_validator(url):
            calls.append(url)
            raise Web3ValidationError(f"Rejected: {url}")

        with pytest.raises(Web3ValidationError, match="Rejected"):
            reject_validator("https://example.com/api")

        assert len(calls) == 1
        assert calls[0] == "https://example.com/api"

    def test_custom_validator_can_allow(self):
        calls = []

        def allow_validator(url):
            calls.append(url)

        allow_validator("https://example.com/api")
        assert len(calls) == 1
