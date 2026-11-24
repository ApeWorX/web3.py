import pytest
import asyncio

from web3 import (
    AsyncWeb3,
    Web3,
)
from web3.exceptions import (
    Web3RPCError,
    Web3ValueError,
)
from web3.providers import (
    AsyncHTTPProvider,
    AsyncIPCProvider,
    HTTPProvider,
)


def test_manual_batch_releases_provider_after_rpc_error(mocker):
    w3 = Web3(HTTPProvider())
    mocker.patch.object(
        w3.provider,
        "make_batch_request",
        return_value=[
            {"jsonrpc": "2.0", "id": 0, "error": {"code": -32000, "message": "busy"}}
        ],
    )
    request = mocker.patch.object(
        w3.provider,
        "make_request",
        return_value={"jsonrpc": "2.0", "id": 1, "result": "0x2a"},
    )
    batch = w3.batch_requests()
    batch.add(w3.eth.block_number)
    with pytest.raises(Web3RPCError, match="busy"):
        batch.execute()

    assert w3.eth.block_number == 42
    request.assert_called_once()
    with pytest.raises(Web3ValueError, match="already been executed or cancelled"):
        batch.execute()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", [OSError("connection closed"), asyncio.CancelledError()]
)
async def test_manual_async_batch_releases_provider_on_failure(mocker, failure):
    w3 = AsyncWeb3(AsyncHTTPProvider())
    mocker.patch.object(w3.provider, "make_batch_request", side_effect=failure)
    request = mocker.patch.object(
        w3.provider,
        "make_request",
        return_value={"jsonrpc": "2.0", "id": 1, "result": "0x2a"},
    )
    batch = w3.batch_requests()
    batch.add(w3.eth.block_number)
    with pytest.raises(type(failure)):
        await batch.async_execute()

    assert await w3.eth.block_number == 42
    request.assert_awaited_once()
    with pytest.raises(Web3ValueError, match="already been executed or cancelled"):
        await batch.async_execute()


def test_finished_batch_cannot_consume_a_later_batch(mocker):
    w3 = Web3(HTTPProvider())
    send = mocker.patch.object(
        w3.provider,
        "make_batch_request",
        return_value=[{"jsonrpc": "2.0", "id": 0, "result": "0x2a"}],
    )
    finished = w3.batch_requests()
    finished.cancel()
    current = w3.batch_requests()
    current.add(w3.eth.block_number)

    with pytest.raises(Web3ValueError, match="already been executed or cancelled"):
        finished.execute()
    finished.cancel()
    assert current.execute() == [42]
    send.assert_called_once()


@pytest.mark.asyncio
async def test_manual_socket_batch_can_restart_after_write_failure(mocker):
    provider = AsyncIPCProvider()
    w3 = AsyncWeb3(provider)
    mocker.patch.object(provider, "socket_send", side_effect=[OSError("closed"), None])
    mocker.patch.object(
        provider,
        "_get_response_for_request_id",
        return_value=[{"jsonrpc": "2.0", "id": 1, "result": "0x2a"}],
    )
    failed = w3.batch_requests()
    failed.add(w3.eth.block_number)
    with pytest.raises(OSError, match="closed"):
        await failed.async_execute()

    with pytest.raises(Web3ValueError, match="already been executed or cancelled"):
        await failed.async_execute()
    retry = w3.batch_requests()
    retry.add(w3.eth.block_number)
    assert await retry.async_execute() == [42]
