import pytest
import json
import os
from pathlib import (
    Path,
)
import re
import subprocess
import time
import zipfile

from eth_utils import (
    is_dict,
)
import pytest_asyncio

from web3._utils.contract_sources.contract_data.emitter_contract import (
    EMITTER_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.math_contract import (
    MATH_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.panic_errors_contract import (
    PANIC_ERRORS_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.revert_contract import (
    REVERT_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.storage_contract import (
    STORAGE_CONTRACT_DATA,
)

from .utils import (
    kill_proc_gracefully,
)

KEYFILE_PW = "web3py-test"
GETH_FIXTURE_ZIP = "geth-1.16.7-fixture.zip"


@pytest.fixture
def geth_binary():
    from geth.install import (
        get_executable_path,
        install_geth,
    )

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


def absolute_datadir(directory_name):
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            directory_name,
        )
    )


@pytest.fixture
def get_geth_version(geth_binary):
    from geth import (
        get_geth_version,
    )

    geth_version = get_geth_version(geth_executable=os.path.expanduser(geth_binary))

    fixture_geth_version = GETH_FIXTURE_ZIP.split("-")[1]
    if fixture_geth_version not in str(geth_version):
        raise AssertionError(
            f"geth fixture version `{fixture_geth_version}` does not match geth "
            f"version for binary being used to run the test suite: `{geth_version}`. "
            "For CI runs, make sure to update the geth version in the CI config file."
        )

    return geth_version


@pytest.fixture
def base_geth_command_arguments(geth_binary, datadir):
    return (
        geth_binary,
        "--datadir",
        datadir,
        "--dev",
        "--dev.period",
        "3",
        "--password",
        os.path.join(datadir, "keystore", "pw.txt"),
        # in order to raise on underpriced transactions, ``txpool.nolocals`` is now
        # necessary: https://github.com/ethereum/go-ethereum/pull/31202
        "--txpool.nolocals",
        # Geth's filtermaps log index can race with ``--dev.period`` mining and
        # fail ``eth_getLogs`` topic queries with
        # ``failed to retrieve log value pointer ... pebble: not found``.
        # Tests only need correct log results, so skip the index.
        "--history.logs.disable",
    )


@pytest.fixture
def geth_zipfile_version(get_geth_version):
    # TODO: Remove support for 13 + 14 in next major version
    if get_geth_version.major == 1 and get_geth_version.minor in [13, 14, 15, 16]:
        return GETH_FIXTURE_ZIP
    raise AssertionError("Unsupported geth version")


@pytest.fixture
def datadir(tmpdir_factory, geth_zipfile_version):
    zipfile_path = absolute_datadir(geth_zipfile_version)
    base_dir = tmpdir_factory.mktemp("goethereum")
    tmp_datadir = os.path.join(str(base_dir), "datadir")
    with zipfile.ZipFile(zipfile_path, "r") as zip_ref:
        zip_ref.extractall(tmp_datadir)
    return tmp_datadir


@pytest.fixture
def geth_fixture_data(datadir):
    config_file_path = Path(datadir) / "config.json"
    return json.loads(config_file_path.read_text())


@pytest.fixture
def genesis_file(datadir):
    genesis_file_path = os.path.join(datadir, "genesis.json")
    return genesis_file_path


def wait_for_port(proc, timeout=10):
    start = time.time()
    wait_time = start + timeout

    while time.time() < wait_time:
        line = proc.stderr.readline()
        if not line:
            continue
        elif "geth.ipc" in line:
            # ipc path will be retrieved via ``get_ipc_path()`` fixture
            return None
        elif match := re.compile(r"127\.0\.0\.1:(\d+)").search(line):
            port = int(match.group(1))
            if port not in {0, 80}:
                # remove false positive matches
                return port

    raise TimeoutError(f"Did not find port in logs within {timeout} seconds")


@pytest.fixture
def start_geth_process_and_yield_port(
    geth_binary, datadir, genesis_file, geth_command_arguments
):
    init_cmd = (
        geth_binary,
        "--datadir",
        str(datadir),
        "init",
        str(genesis_file),
    )
    subprocess.check_output(init_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    proc = subprocess.Popen(
        geth_command_arguments,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        port = wait_for_port(proc)
        yield port
    finally:
        # Ensure cleanup happens even if test fails
        kill_proc_gracefully(proc)
        output, errors = proc.communicate(timeout=5)
        print(f"Geth Process Exited:\nstdout: {output}\n\nstderr: {errors}\n\n")


@pytest.fixture
def math_contract_deploy_txn_hash(geth_fixture_data):
    return geth_fixture_data["math_deploy_txn_hash"]


@pytest.fixture
def math_contract(math_contract_factory, geth_fixture_data):
    return math_contract_factory(address=geth_fixture_data["math_address"])


@pytest.fixture
def math_contract_address(math_contract, address_conversion_func):
    return address_conversion_func(math_contract.address)


@pytest.fixture
def emitter_contract(emitter_contract_factory, geth_fixture_data):
    return emitter_contract_factory(address=geth_fixture_data["emitter_address"])


@pytest.fixture
def emitter_contract_address(emitter_contract, address_conversion_func):
    return address_conversion_func(emitter_contract.address)


@pytest.fixture
def keyfile_account_pkey(geth_fixture_data):
    return geth_fixture_data["keyfile_account_pkey"]


@pytest.fixture
def keyfile_account_address(geth_fixture_data):
    return geth_fixture_data["keyfile_account_address"]


@pytest.fixture
def keyfile_account_address_dual_type(keyfile_account_address, address_conversion_func):
    yield keyfile_account_address


@pytest.fixture
def empty_block(w3, geth_fixture_data):
    block = w3.eth.get_block(geth_fixture_data["empty_block_hash"])
    assert is_dict(block)
    return block


@pytest.fixture
def block_with_txn(w3, geth_fixture_data):
    block = w3.eth.get_block(geth_fixture_data["block_with_txn_hash"])
    assert is_dict(block)
    return block


@pytest.fixture
def mined_txn_hash(geth_fixture_data):
    return geth_fixture_data["mined_txn_hash"]


@pytest.fixture
def block_with_txn_with_log(w3, geth_fixture_data):
    block = w3.eth.get_block(geth_fixture_data["block_hash_with_log"])
    assert is_dict(block)
    return block


@pytest.fixture
def txn_hash_with_log(geth_fixture_data):
    return geth_fixture_data["txn_hash_with_log"]


@pytest.fixture
def block_hash_revert_no_msg(geth_fixture_data):
    return geth_fixture_data["block_hash_revert_no_msg"]


@pytest.fixture
def block_hash_revert_with_msg(geth_fixture_data):
    return geth_fixture_data["block_hash_revert_with_msg"]


@pytest.fixture
def revert_contract(revert_contract_factory, geth_fixture_data):
    return revert_contract_factory(address=geth_fixture_data["revert_address"])


@pytest.fixture
def offchain_lookup_contract(offchain_lookup_contract_factory, geth_fixture_data):
    return offchain_lookup_contract_factory(
        address=geth_fixture_data["offchain_lookup_address"]
    )


@pytest.fixture
def panic_errors_contract(
    w3,
    geth_fixture_data,
):
    contract_factory = w3.eth.contract(**PANIC_ERRORS_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["panic_errors_contract_address"])


@pytest.fixture
def storage_contract(
    w3,
    geth_fixture_data,
):
    contract_factory = w3.eth.contract(**STORAGE_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["storage_contract_address"])


# --- async --- #


@pytest_asyncio.fixture
async def async_keyfile_account_address(geth_fixture_data):
    return geth_fixture_data["keyfile_account_address"]


@pytest_asyncio.fixture
async def async_keyfile_account_address_dual_type(
    async_keyfile_account_address, address_conversion_func
):
    yield async_keyfile_account_address


@pytest.fixture
def async_offchain_lookup_contract(
    async_offchain_lookup_contract_factory, geth_fixture_data
):
    return async_offchain_lookup_contract_factory(
        address=geth_fixture_data["offchain_lookup_address"]
    )


@pytest.fixture
def async_panic_errors_contract(
    async_w3,
    geth_fixture_data,
):
    contract_factory = async_w3.eth.contract(**PANIC_ERRORS_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["panic_errors_contract_address"])


@pytest.fixture
def async_emitter_contract(async_w3, geth_fixture_data):
    contract_factory = async_w3.eth.contract(**EMITTER_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["emitter_address"])


@pytest.fixture
def async_emitter_contract_address(async_emitter_contract, address_conversion_func):
    return address_conversion_func(async_emitter_contract.address)


@pytest.fixture
def async_math_contract(async_w3, geth_fixture_data):
    contract_factory = async_w3.eth.contract(**MATH_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["math_address"])


@pytest.fixture
def async_math_contract_address(async_math_contract, address_conversion_func):
    return address_conversion_func(async_math_contract.address)


@pytest.fixture
def async_revert_contract(async_w3, geth_fixture_data):
    contract_factory = async_w3.eth.contract(**REVERT_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["revert_address"])


@pytest.fixture
def async_storage_contract(
    async_w3,
    geth_fixture_data,
):
    contract_factory = async_w3.eth.contract(**STORAGE_CONTRACT_DATA)
    return contract_factory(address=geth_fixture_data["storage_contract_address"])


@pytest_asyncio.fixture
async def async_empty_block(async_w3, geth_fixture_data):
    block = await async_w3.eth.get_block(geth_fixture_data["empty_block_hash"])
    assert is_dict(block)
    return block


@pytest_asyncio.fixture
async def async_block_with_txn(async_w3, geth_fixture_data):
    block = await async_w3.eth.get_block(geth_fixture_data["block_with_txn_hash"])
    assert is_dict(block)
    return block


@pytest_asyncio.fixture
async def async_block_with_txn_with_log(async_w3, geth_fixture_data):
    block = await async_w3.eth.get_block(geth_fixture_data["block_hash_with_log"])
    assert is_dict(block)
    return block
