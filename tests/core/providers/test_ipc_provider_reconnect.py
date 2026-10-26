import pytest
import errno
from unittest.mock import (
    AsyncMock,
    Mock,
    patch,
)

from web3.providers import (
    AsyncIPCProvider,
)
from web3.providers.ipc import (
    IPCProvider,
)

REQUEST = b'{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":0}'
RESPONSE = b'{"id":0,"jsonrpc":"2.0","result":"0x1"}'


def test_ipc_retry_after_broken_pipe_keeps_newline_delimiter():
    provider = IPCProvider("unused.ipc")
    broken_socket = Mock()
    broken_socket.sendall.side_effect = BrokenPipeError()
    replacement_socket = Mock()
    replacement_socket.recv.return_value = RESPONSE
    provider._socket.sock = broken_socket

    with patch.object(provider._socket, "_open", return_value=replacement_socket):
        response = provider._make_request(REQUEST)

    assert response == {"id": 0, "jsonrpc": "2.0", "result": "0x1"}
    broken_socket.sendall.assert_called_once_with(REQUEST + b"\n")
    replacement_socket.sendall.assert_called_once_with(REQUEST + b"\n")


@pytest.mark.asyncio
async def test_async_ipc_retry_after_broken_pipe_keeps_newline_delimiter():
    provider = AsyncIPCProvider("unused.ipc")
    broken_writer = Mock()
    broken_writer.drain = AsyncMock(side_effect=OSError(errno.EPIPE, "broken pipe"))
    replacement_writer = Mock()
    replacement_writer.drain = AsyncMock()
    provider._writer = broken_writer

    async def reset_socket():
        provider._writer = replacement_writer

    provider._reset_socket = AsyncMock(side_effect=reset_socket)
    await provider._socket_send(REQUEST)

    broken_writer.write.assert_called_once_with(REQUEST + b"\n")
    provider._reset_socket.assert_awaited_once()
    replacement_writer.write.assert_called_once_with(REQUEST + b"\n")
    replacement_writer.drain.assert_awaited_once()
