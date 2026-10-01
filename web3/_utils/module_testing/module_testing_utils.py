import asyncio
from collections.abc import Collection, Generator, Sequence
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Union,
)

from aiohttp import (
    ClientSession,
    ClientTimeout,
)
from eth_typing import (
    ChecksumAddress,
    HexStr,
)
from eth_utils import (
    is_same_address,
)
from hexbytes import (
    HexBytes,
)
import requests
from websockets.protocol import (
    State,
)

from web3._utils.http import (
    DEFAULT_HTTP_TIMEOUT,
)
from web3.types import (
    BlockData,
    LogReceipt,
)

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch  # noqa: F401
    from aiohttp import (  # noqa: F401
        ClientResponse,
    )
    from requests import Response  # noqa: F401

    from web3._utils.compat import (  # noqa: F401
        Self,
    )


def assert_contains_log(
    result: Sequence[LogReceipt],
    block_with_txn_with_log: BlockData,
    emitter_contract_address: ChecksumAddress,
    txn_hash_with_log: HexStr,
) -> None:
    assert len(result) > 0
    log_entry = result[0]
    assert log_entry["blockNumber"] == block_with_txn_with_log["number"]
    assert log_entry["blockHash"] == block_with_txn_with_log["hash"]
    assert log_entry["logIndex"] == 0
    assert is_same_address(log_entry["address"], emitter_contract_address)
    assert log_entry["transactionIndex"] == 0
    assert log_entry["transactionHash"] == HexBytes(txn_hash_with_log)


def _mock_getaddrinfo_public(
    monkeypatch: "MonkeyPatch",
) -> None:
    # Patch socket.getaddrinfo to return a public IP for CCIP test domains
    # so that CCIP URL host validation passes during tests. Pass through
    # to the real getaddrinfo for all other hosts (e.g. 127.0.0.1 for geth).
    import socket as _socket

    _original_getaddrinfo = _socket.getaddrinfo

    def _patched_getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        if host == "web3.py":
            return [(_socket.AF_INET, _socket.SOCK_STREAM, 0, "", ("1.2.3.4", 0))]
        return _original_getaddrinfo(host, port, *args, **kwargs)

    monkeypatch.setattr("socket.getaddrinfo", _patched_getaddrinfo)


def mock_offchain_lookup_request_response(
    monkeypatch: "MonkeyPatch",
    http_method: Literal["GET", "POST"] = "GET",
    mocked_request_url: str = None,
    mocked_status_code: int = 200,
    mocked_json_data: str = "0x",
    json_data_field: str = "data",
    # required only for POST validation:
    sender: str = None,
    calldata: str = None,
) -> None:
    _mock_getaddrinfo_public(monkeypatch)

    class MockedResponse:
        status_code = mocked_status_code

        @staticmethod
        def json() -> dict[str, str]:
            return {json_data_field: mocked_json_data}  # noqa: E704

        @staticmethod
        def raise_for_status() -> None:
            raise Exception("called raise_for_status()")  # noqa: E704

    def _mock_specific_request(
        *args: Any, **kwargs: Any
    ) -> Union["Response", MockedResponse]:
        url_from_args = args[1]

        # mock response only to specified url while validating appropriate fields
        if url_from_args == mocked_request_url:
            assert kwargs["timeout"] == DEFAULT_HTTP_TIMEOUT
            assert kwargs.get("allow_redirects") is False
            if http_method.upper() == "POST":
                assert kwargs["json"] == {"data": calldata, "sender": sender}
            return MockedResponse()

        # else, make a normal request (no mocking)
        session = requests.Session()
        return session.request(method=http_method.upper(), url=url_from_args, **kwargs)

    monkeypatch.setattr(
        f"requests.Session.{http_method.lower()}", _mock_specific_request
    )


# -- async -- #


def async_mock_offchain_lookup_request_response(
    monkeypatch: "MonkeyPatch",
    http_method: Literal["GET", "POST"] = "GET",
    mocked_request_url: str = None,
    mocked_status_code: int = 200,
    mocked_json_data: str = "0x",
    json_data_field: str = "data",
    # required only for POST validation:
    sender: str = None,
    calldata: str = None,
) -> None:
    _mock_getaddrinfo_public(monkeypatch)

    class AsyncMockedResponse:
        status = mocked_status_code

        def __await__(self) -> Generator[Any, Any, Any]:
            yield
            return self

        @staticmethod
        async def json() -> dict[str, str]:
            return {json_data_field: mocked_json_data}  # noqa: E704

        @staticmethod
        def raise_for_status() -> None:
            raise Exception("called raise_for_status()")  # noqa: E704

    async def _mock_specific_request(
        *args: Any, **kwargs: Any
    ) -> Union["ClientResponse", AsyncMockedResponse]:
        url_from_args = args[1]

        # mock response only to specified url while validating appropriate fields
        if url_from_args == mocked_request_url:
            assert kwargs["timeout"] == ClientTimeout(DEFAULT_HTTP_TIMEOUT)
            assert kwargs.get("allow_redirects") is False
            if http_method.upper() == "POST":
                assert kwargs["json"] == {"data": calldata, "sender": sender}
            return AsyncMockedResponse()

        # else, make a normal request (no mocking)
        session = ClientSession()
        response = await session.request(
            method=http_method.upper(), url=url_from_args, **kwargs
        )
        await session.close()
        return response

    monkeypatch.setattr(
        f"aiohttp.ClientSession.{http_method.lower()}", _mock_specific_request
    )


class WebSocketMessageStreamMock:
    state: State = State.OPEN

    def __init__(
        self,
        messages: Collection[bytes] = None,
        raise_exception: Exception = None,
    ) -> None:
        self.queue = asyncio.Queue()  # type: ignore  # py38 issue
        for msg in messages or []:
            self.queue.put_nowait(msg)
        self.raise_exception = raise_exception

    def __await__(self) -> Generator[Any, Any, "Self"]:
        async def __async_init__() -> "Self":
            return self

        return __async_init__().__await__()

    def __aiter__(self) -> "Self":
        return self

    async def __anext__(self) -> bytes:
        return await self.queue.get()

    async def recv(self) -> bytes:
        if self.raise_exception:
            raise self.raise_exception
        return await self.queue.get()

    @staticmethod
    async def pong() -> Literal[False]:
        return False

    async def connect(self) -> None:
        pass

    async def send(self, data: bytes) -> None:
        pass

    async def close(self) -> None:
        pass
