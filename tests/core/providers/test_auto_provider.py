import pytest
import os
import sys

from web3.providers import (
    HTTPProvider,
    IPCProvider,
)
from web3.providers.auto import (
    load_provider_from_environment,
)
from web3.providers.ipc import (
    get_dev_ipc_path,
)

# Ugly hack to import infura now that API KEY is required
os.environ["WEB3_INFURA_PROJECT_ID"] = "test"


@pytest.fixture(autouse=True)
def delete_environment_variables(monkeypatch):
    monkeypatch.delenv("WEB3_INFURA_PROJECT_ID", raising=False)
    monkeypatch.delenv("WEB3_INFURA_API_SECRET", raising=False)
    monkeypatch.delenv("WEB3_INFURA_SCHEME", raising=False)


@pytest.mark.parametrize(
    "uri, expected_type, expected_attrs",
    (
        ("", type(None), {}),
        ("http://1.2.3.4:5678", HTTPProvider, {"endpoint_uri": "http://1.2.3.4:5678"}),
        (
            "https://node.ontheweb.com",
            HTTPProvider,
            {"endpoint_uri": "https://node.ontheweb.com"},
        ),
        pytest.param(
            "file:///root/path/to/file.ipc",
            IPCProvider,
            {"ipc_path": "/root/path/to/file.ipc"},
            marks=pytest.mark.skipif(
                sys.platform == "win32",
                reason="Unix domain sockets are not supported on Windows",
            ),
        ),
    ),
)
def test_load_provider_from_env(monkeypatch, uri, expected_type, expected_attrs):
    monkeypatch.setenv("WEB3_PROVIDER_URI", uri)
    provider = load_provider_from_environment()
    assert isinstance(provider, expected_type)
    for attr, val in expected_attrs.items():
        assert getattr(provider, attr) == val


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix domain sockets are not supported on Windows"
)
def test_get_dev_ipc_path(monkeypatch, tmp_path):
    # test default path
    monkeypatch.delenv("TMPDIR", raising=False)
    path = get_dev_ipc_path()
    assert path == "/tmp/geth.ipc"

    uri = str(tmp_path) + "/geth.ipc"

    # test setting the "TMPDIR" environment variable
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    path = get_dev_ipc_path()
    assert path == uri
    monkeypatch.delenv("TMPDIR")  # reset

    # test with WEB3_PROVIDER_URI set
    monkeypatch.setenv("WEB3_PROVIDER_URI", uri)
    path = get_dev_ipc_path()
    assert path == uri
