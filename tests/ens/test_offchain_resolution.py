import pytest
import socket

from aiohttp import (
    ClientSession,
)
import requests

from ens.utils import (
    dns_encode_name,
)
from web3.exceptions import (
    OffchainLookup,
    Web3ValidationError,
)


def _mock_getaddrinfo_public(monkeypatch):
    """Patch socket.getaddrinfo to return a public IP for CCIP test domains."""
    _original = socket.getaddrinfo

    def _patched(host, port, *args, **kwargs):
        if host == "web3.py":
            return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("1.2.3.4", 0))]
        return _original(host, port, *args, **kwargs)

    monkeypatch.setattr("socket.getaddrinfo", _patched)


# the encoded calldata for the initiating ``addr(namehash(name))`` call
ENCODED_ADDR_CALLDATA = (
    "0x3b3b57de42041b0018edd29d7c17154b0c671acc0502ea0b3693cafbeadf58e6beaaa16c"  # noqa: E501
)

# This is one of the actual returned payloads from the GET request that
# is triggered when resolving ``ns.address('offchainexample.eth')``
# on mainnet. Since we got rid of the time expiration constraint for our
# OffchainResolver.sol, this hash ends up working for our local test
# case as well since the signer is able to be recovered.
OFFCHAIN_RESOLVER_DATA = (
    "0x0000000000000000000000000000000000000000000000000000000000000060"
    "000000000000000000000000000000000000000000000000000000006271abd2"
    "00000000000000000000000000000000000000000000000000000000000000a0"
    "0000000000000000000000000000000000000000000000000000000000000020"
    "000000000000000000000000d8da6bf26964af9d7eed9e03e53415d37aa96045"
    "0000000000000000000000000000000000000000000000000000000000000040"
    "1774ff038dbf6d7a5e5924c00d739f507c7d3ca6bf6c99abaf7d2f0042f00b75"
    "e30fdda27b9291dc035b38114d08495ca5d70f3c859facaa23b06c39b6757034"
)

EXPECTED_GET_URL = (
    "https://web3.py/gateway/0x05ca7c4bc9886f11ae031d5c397a8b4827b4a4fd/0x9061b923000"
    "00000000000000000000000000000000000000000000000000000000000400000000000000000000"
    "00000000000000000000000000000000000000000008000000000000000000000000000000000000"
    "000000000000000000000000000150f6f6666636861696e6578616d706c650365746800000000000"
    "000000000000000000000000000000000000000000000000000000000000000000000000000243b3"
    "b57de42041b0018edd29d7c17154b0c671acc0502ea0b3693cafbeadf58e6beaaa16c00000000000"
    "000000000000000000000000000000000000000000000.json"
)
EXPECTED_POST_URL = (
    "https://web3.py/gateway/0x05ca7c4bc9886f11ae031d5c397a8b4827b4a4fd.json"
)
EXPECTED_RESOLVED_ADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"


class MockHttpSuccessResponse:
    status_code = 200

    def __init__(self, request_type, *args, **_kwargs):
        # validate the expected urls
        if request_type == "get":
            assert args[1] == EXPECTED_GET_URL
        elif request_type == "post":
            assert args[1] == EXPECTED_POST_URL

    @staticmethod
    def raise_for_status():
        pass  # noqa: E704

    @staticmethod
    def json():
        return {"data": OFFCHAIN_RESOLVER_DATA}  # noqa: E704


class MockHttpBadFormatResponse:
    status_code = 200

    def __init__(self, *args):
        assert args[1] == EXPECTED_GET_URL

    @staticmethod
    def raise_for_status():
        pass  # noqa: E704

    @staticmethod
    def json():
        return {"not_data": OFFCHAIN_RESOLVER_DATA}  # noqa: E704


class AsyncMockHttpSuccessResponse:
    status_code = 200

    def __init__(self, request_type, *args, **_kwargs):
        # validate the expected urls
        if request_type == "get":
            assert args[1] == EXPECTED_GET_URL
        elif request_type == "post":
            assert args[1] == EXPECTED_POST_URL

    @staticmethod
    def raise_for_status():
        pass  # noqa: E704

    @staticmethod
    async def json():
        return {"data": OFFCHAIN_RESOLVER_DATA}  # noqa: E704

    @property
    def status(self):
        return self.status_code


class AsyncMockHttpBadFormatResponse:
    status_code = 200

    def __init__(self, *args):
        assert args[1] == EXPECTED_GET_URL

    @staticmethod
    def raise_for_status():
        pass  # noqa: E704

    @staticmethod
    async def json():
        return {"not_data": OFFCHAIN_RESOLVER_DATA}  # noqa: E704

    @property
    def status(self):
        return self.status_code


def test_offchain_resolution_with_get_request(ens, monkeypatch):
    _mock_getaddrinfo_public(monkeypatch)

    # mock GET response with real return data from 'offchainexample.eth' resolver
    def mock_get(*args, **kwargs):
        return MockHttpSuccessResponse("get", *args, **kwargs)

    monkeypatch.setattr(requests.Session, "get", mock_get)

    assert ens.address("offchainexample.eth") == EXPECTED_RESOLVED_ADDRESS


def test_offchain_resolution_with_post_request(ens, monkeypatch):
    _mock_getaddrinfo_public(monkeypatch)

    # mock POST response with real return data from 'offchainexample.eth' resolver
    def mock_post(*args, **kwargs):
        return MockHttpSuccessResponse("post", *args, **kwargs)

    monkeypatch.setattr(requests.Session, "post", mock_post)

    assert ens.address("offchainexample.eth") == EXPECTED_RESOLVED_ADDRESS


def test_offchain_resolution_raises_when_all_supplied_urls_fail(ens):
    # with no mocked responses, requests to all urls will fail
    with pytest.raises(Exception, match="Offchain lookup failed for supplied urls."):
        ens.address("offchainexample.eth")


def test_offchain_resolution_with_improperly_formatted_http_response(ens, monkeypatch):
    _mock_getaddrinfo_public(monkeypatch)

    def mock_get(*args, **_):
        return MockHttpBadFormatResponse(*args)

    monkeypatch.setattr(requests.Session, "get", mock_get)
    with pytest.raises(
        Web3ValidationError,
        match=(
            "Improperly formatted response for offchain lookup HTTP request "
            "- missing 'data' field."
        ),
    ):
        ens.address("offchainexample.eth")


def test_offchain_resolver_function_call_raises_with_ccip_read_disabled(
    ens, monkeypatch
):
    offchain_resolver = ens.resolver("offchainexample.eth")

    # should fail here with `ccip_read_enabled` flag set to False
    with pytest.raises(OffchainLookup):
        offchain_resolver.functions.resolve(
            dns_encode_name("offchainexample.eth"),
            ENCODED_ADDR_CALLDATA,
        ).call(ccip_read_enabled=False)

    # pass flag on specific call via ContractCaller is also an option
    with pytest.raises(OffchainLookup):
        offchain_resolver.caller(ccip_read_enabled=False).resolve(
            dns_encode_name("offchainexample.eth"),
            ENCODED_ADDR_CALLDATA,
        )


# -- async -- #


@pytest.mark.asyncio
async def test_async_offchain_resolution_with_get_request(async_ens, monkeypatch):
    _mock_getaddrinfo_public(monkeypatch)

    # mock GET response with real return data from 'offchainexample.eth' resolver
    async def mock_get(*args, **kwargs):
        return AsyncMockHttpSuccessResponse("get", *args, **kwargs)

    monkeypatch.setattr(ClientSession, "get", mock_get)

    assert await async_ens.address("offchainexample.eth") == EXPECTED_RESOLVED_ADDRESS


@pytest.mark.asyncio
async def test_async_offchain_resolution_with_post_request(async_ens, monkeypatch):
    _mock_getaddrinfo_public(monkeypatch)

    # mock POST response with real return data from 'offchainexample.eth' resolver
    async def mock_post(*args, **kwargs):
        return AsyncMockHttpSuccessResponse("post", *args, **kwargs)

    monkeypatch.setattr(ClientSession, "post", mock_post)

    assert await async_ens.address("offchainexample.eth") == EXPECTED_RESOLVED_ADDRESS


@pytest.mark.asyncio
async def test_async_offchain_resolution_raises_when_all_supplied_urls_fail(async_ens):
    # with no mocked responses, requests to all urls will fail
    with pytest.raises(Exception, match="Offchain lookup failed for supplied urls."):
        await async_ens.address("offchainexample.eth")


@pytest.mark.asyncio
async def test_async_offchain_resolution_with_improperly_formatted_http_response(
    async_ens, monkeypatch
):
    _mock_getaddrinfo_public(monkeypatch)

    async def mock_get(*args, **_):
        return AsyncMockHttpBadFormatResponse(*args)

    monkeypatch.setattr(ClientSession, "get", mock_get)
    with pytest.raises(
        Web3ValidationError,
        match=(
            "Improperly formatted response for offchain lookup HTTP request "
            "- missing 'data' field."
        ),
    ):
        await async_ens.address("offchainexample.eth")
