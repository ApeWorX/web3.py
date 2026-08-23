from collections.abc import Generator, Sequence
import os
import socket
from subprocess import (
    PIPE,
    Popen,
    check_output,
)
from tempfile import (
    TemporaryDirectory,
)
from typing import (
    Any,
)
import zipfile

from geth.install import (
    get_executable_path,
    install_geth,
)

from .utils import (
    kill_proc_gracefully,
)

GETH_FIXTURE_ZIP = "geth-1.16.7-fixture.zip"


class GethBenchmarkFixture:
    def __init__(self) -> None:
        self.rpc_port = self._rpc_port()
        self.endpoint_uri = self._endpoint_uri()
        self.geth_binary = self._geth_binary()

    def build(self) -> Generator[Any, None, None]:
        with TemporaryDirectory() as base_dir:
            zipfile_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../tests/integration/",
                    GETH_FIXTURE_ZIP,
                )
            )
            tmp_datadir = os.path.join(str(base_dir), "datadir")
            with zipfile.ZipFile(zipfile_path, "r") as zip_ref:
                zip_ref.extractall(tmp_datadir)
            self.datadir = tmp_datadir

            genesis_file = os.path.join(self.datadir, "genesis.json")

            yield self._geth_process(self.datadir, genesis_file, self.rpc_port)

    def _rpc_port(self) -> str:
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        return str(port)

    def _endpoint_uri(self) -> str:
        return f"http://localhost:{self.rpc_port}"

    def _geth_binary(self) -> str:
        if "GETH_BINARY" in os.environ:
            return os.environ["GETH_BINARY"]
        elif "GETH_VERSION" in os.environ:
            geth_version = os.environ["GETH_VERSION"]
            _geth_binary = get_executable_path(geth_version)
            if not os.path.exists(_geth_binary):
                install_geth(geth_version)
            assert os.path.exists(_geth_binary)
            return _geth_binary
        else:
            return "geth"

    def _geth_command_arguments(self, datadir: str) -> Sequence[str]:
        return (
            self.geth_binary,
            "--dev",
            "--dev.period",
            "100",
            "--datadir",
            datadir,
            "--nodiscover",
            "--http",
            "--http.port",
            self.rpc_port,
            "--http.api",
            "admin,debug,eth,net,web3",
            "--ipcdisable",
            "--password",
            os.path.join(datadir, "keystore", "pw.txt"),
        )

    def _geth_process(
        self, datadir: str, genesis_file: str, rpc_port: str
    ) -> Generator[Any, None, None]:
        init_datadir_command = (
            self.geth_binary,
            "--datadir",
            str(datadir),
            "init",
            str(genesis_file),
        )
        check_output(
            init_datadir_command,
            stdin=PIPE,
            stderr=PIPE,
        )
        proc = Popen(
            self._geth_command_arguments(datadir),
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
        )
        try:
            yield proc
        finally:
            kill_proc_gracefully(proc)
