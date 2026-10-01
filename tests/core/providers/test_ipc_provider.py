import pytest
import os
import pathlib
import socket
import sys
import tempfile
from threading import (
    Thread,
)
import time
from unittest.mock import (
    Mock,
    patch,
)

from web3.auto.gethdev import (
    w3,
)
from web3.exceptions import (
    ProviderConnectionError,
    Web3ValueError,
)
from web3.providers.ipc import (
    IPCProvider,
    get_default_ipc_path,
    get_dev_ipc_path,
)
from web3.types import (
    RPCEndpoint,
)

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Unix domain sockets are not supported on Windows"
)


@pytest.fixture
def jsonrpc_ipc_pipe_path():
    with tempfile.TemporaryDirectory() as temp_dir:
        ipc_path = os.path.join(temp_dir, "temp.ipc")
        try:
            yield ipc_path
        finally:
            if os.path.exists(ipc_path):
                os.remove(ipc_path)


def test_ipc_no_path():
    """
    IPCProvider.is_connected() returns False when no path is supplied
    """
    ipc = IPCProvider(None)
    assert ipc.is_connected() is False
    with pytest.raises(ProviderConnectionError):
        ipc.is_connected(show_traceback=True)


def test_ipc_tilda_in_path():
    expectedPath = str(pathlib.Path.home()) + "/foo"
    assert IPCProvider("~/foo").ipc_path == expectedPath
    assert IPCProvider(pathlib.Path("~/foo")).ipc_path == expectedPath


@pytest.mark.parametrize(
    "platform, expected_result, expected_error",
    [
        ("darwin", "/Library/Ethereum/geth.ipc", None),
        ("linux", "/.ethereum/geth.ipc", None),
        ("freebsd", "/.ethereum/geth.ipc", None),
        ("win32", r"\\.\pipe\geth.ipc", None),
        (
            "unknown",
            None,
            {
                "error": Web3ValueError,
                "match": (
                    "Unsupported platform 'unknown'. Only darwin/linux/win32/"
                    "freebsd are supported.  You must specify the ipc_path"
                ),
            },
        ),
    ],
)
def test_get_default_ipc_path(platform, expected_result, expected_error):
    with patch.object(sys, "platform", platform):
        if expected_error:
            with pytest.raises(expected_error["error"], match=expected_error["match"]):
                get_default_ipc_path()
        else:
            assert get_default_ipc_path().endswith(expected_result)


@pytest.mark.parametrize(
    "provider_env_uri",
    [
        "/sample/path/to/ipc/geth.ipc",
        "",
    ],
)
@pytest.mark.parametrize(
    "platform, expected_result, expected_error",
    [
        ("darwin", "/var/path/to/tmp/T/geth.ipc", None),
        ("linux", "/var/path/to/tmp/T/geth.ipc", None),
        ("freebsd", "/tmp/geth.ipc", None),
        ("win32", r"\\.\pipe\geth.ipc", None),
        (
            "unknown",
            None,
            {
                "error": Web3ValueError,
                "match": (
                    "Unsupported platform 'unknown'. Only darwin/linux/win32/"
                    "freebsd are supported.  You must specify the ipc_path"
                ),
            },
        ),
    ],
)
def test_get_dev_ipc_path_(provider_env_uri, platform, expected_result, expected_error):
    with patch.object(sys, "platform", platform):
        with patch.dict(
            os.environ,
            {
                "TMPDIR": "/var/path/to/tmp/T/",
                "WEB3_PROVIDER_URI": provider_env_uri or "",
            },
        ):
            if provider_env_uri:
                assert get_dev_ipc_path() == provider_env_uri
            elif expected_error:
                with pytest.raises(
                    expected_error["error"], match=expected_error["match"]
                ):
                    get_dev_ipc_path()
            else:
                assert get_dev_ipc_path() == expected_result


@pytest.fixture
def simple_ipc_server(jsonrpc_ipc_pipe_path):
    serv = socket.socket(socket.AF_UNIX)
    serv.bind(jsonrpc_ipc_pipe_path)
    serv.listen(1)
    try:
        yield serv
    finally:
        serv.close()


@pytest.fixture
def serve_empty_result(simple_ipc_server):
    def reply():
        connection, client_address = simple_ipc_server.accept()
        try:
            connection.recv(1024)
            connection.sendall(b'{"id":1, "result": {}')
            time.sleep(0.1)
            connection.sendall(b"}")
        finally:
            # Clean up the connection
            connection.close()
            simple_ipc_server.close()

    thd = Thread(target=reply, daemon=True)
    thd.start()

    try:
        yield
    finally:
        thd.join()


def test_sync_waits_for_full_result(jsonrpc_ipc_pipe_path, serve_empty_result):
    provider = IPCProvider(pathlib.Path(jsonrpc_ipc_pipe_path), timeout=3)
    result = provider.make_request("method", [])
    assert result == {"id": 1, "result": {}}
    provider._socket.sock.close()


def test_web3_auto_gethdev(request_mocker):
    assert isinstance(w3.provider, IPCProvider)
    with request_mocker(
        w3,
        mock_results={
            RPCEndpoint("eth_getBlockByNumber"): {"extraData": "0x" + "ff" * 33}
        },
    ):
        block = w3.eth.get_block("latest")

    assert "extraData" not in block
    assert block.proofOfAuthorityData == b"\xff" * 33


def test_ipc_provider_write_messages_end_with_new_line_delimiter(jsonrpc_ipc_pipe_path):
    provider = IPCProvider(pathlib.Path(jsonrpc_ipc_pipe_path), timeout=3)
    provider._socket.sock = Mock()
    provider._socket.sock.recv.return_value = (
        b'{"id":0, "jsonrpc": "2.0", "result": {}}\n'
    )

    provider.make_request("method", [])

    request_data = b'{"jsonrpc": "2.0", "method": "method", "params": [], "id": 0}'
    provider._socket.sock.sendall.assert_called_with(request_data + b"\n")
