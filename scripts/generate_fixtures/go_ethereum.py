import contextlib
import json
import os
import pprint
import re
import shutil
import socket
import subprocess
import time

from eth_utils.curried import (
    apply_formatter_if,
    is_bytes,
    is_dict,
    to_hex,
    to_text,
)
from eth_utils.toolz import (
    merge,
    valmap,
)

from web3 import (
    Web3,
)
from web3._utils.contract_sources.contract_data._custom_contract_data import (
    EMITTER_ENUM,
)
from web3._utils.contract_sources.contract_data.emitter_contract import (
    EMITTER_CONTRACT_ABI,
    EMITTER_CONTRACT_BYTECODE,
)
from web3._utils.contract_sources.contract_data.math_contract import (
    MATH_CONTRACT_ABI,
    MATH_CONTRACT_BYTECODE,
)
from web3._utils.contract_sources.contract_data.offchain_lookup import (
    OFFCHAIN_LOOKUP_ABI,
    OFFCHAIN_LOOKUP_BYTECODE,
)
from web3._utils.contract_sources.contract_data.panic_errors_contract import (
    PANIC_ERRORS_CONTRACT_DATA,
)
from web3._utils.contract_sources.contract_data.revert_contract import (
    REVERT_CONTRACT_ABI,
    REVERT_CONTRACT_BYTECODE,
)
from web3._utils.contract_sources.contract_data.storage_contract import (
    STORAGE_CONTRACT_DATA,
)
from web3.exceptions import (
    Web3ValueError,
)

from . import common


def get_open_port():
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return str(port)


@contextlib.contextmanager
def graceful_kill_on_exit(proc):
    try:
        yield proc
    finally:
        common.kill_proc_gracefully(proc)


@contextlib.contextmanager
def get_geth_process(geth_binary, datadir, geth_port):
    init_datadir_command = (
        geth_binary,
        "--datadir",
        datadir,
        "init",
        os.path.join(datadir, "genesis.json"),
    )
    subprocess.check_output(
        init_datadir_command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    run_geth_command = (
        geth_binary,
        "--datadir",
        datadir,
        "--dev",
        "--dev.period",
        "1",
        "--port",
        geth_port,
        "--password",
        os.path.join(datadir, "keystore", "pw.txt"),
    )

    popen_proc = subprocess.Popen(
        run_geth_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    with popen_proc as proc:
        with graceful_kill_on_exit(proc) as graceful_proc:
            yield graceful_proc

        output, errors = proc.communicate()

    print(
        "Geth Process Exited:\n"
        f"stdout:{to_text(output)}\n\n"
        f"stderr:{to_text(errors)}\n\n"
    )


def write_config_json(config, datadir):
    bytes_to_hex = apply_formatter_if(is_bytes, to_hex)
    config_json_dict = valmap(bytes_to_hex, config)

    config_path = os.path.join(datadir, "config.json")
    with open(config_path, "w") as config_file:
        config_file.write(json.dumps(config_json_dict))
        config_file.write("\n")


def generate_go_ethereum_fixture(destination_dir):
    with contextlib.ExitStack() as stack:
        datadir = stack.enter_context(common.tempdir())

        keystore_dir = os.path.join(datadir, "keystore")
        common.ensure_path_exists(keystore_dir)
        keyfile_path = os.path.join(keystore_dir, common.KEYFILE_FILENAME)
        with open(keyfile_path, "w") as keyfile:
            keyfile.write(common.KEYFILE_DATA)
        keyfile_pw = os.path.join(keystore_dir, common.KEYFILE_PW_TXT)
        with open(keyfile_pw, "w") as keyfile_pw_file:
            keyfile_pw_file.write(common.KEYFILE_PW)
        genesis_file_path = os.path.join(datadir, "genesis.json")
        with open(genesis_file_path, "w") as genesis_file:
            genesis_file.write(json.dumps(common.GENESIS_DATA))

        geth_ipc_path = f"{datadir}/geth.ipc"
        geth_port = get_open_port()
        geth_binary = common.get_geth_binary()

        with get_geth_process(
            geth_binary=geth_binary,
            datadir=datadir,
            geth_port=geth_port,
        ):
            common.wait_for_socket(geth_ipc_path)
            w3 = Web3(Web3.IPCProvider(geth_ipc_path))
            chain_data = setup_chain_state(w3)
            # close geth by exiting context
            # must be closed before copying data dir
            verify_chain_state(w3, chain_data)

        # verify that chain state is still valid after closing
        # and re-opening geth
        with get_geth_process(
            geth_binary=geth_binary,
            datadir=datadir,
            geth_port=geth_port,
        ):
            common.wait_for_socket(geth_ipc_path)
            w3 = Web3(Web3.IPCProvider(geth_ipc_path))
            verify_chain_state(w3, chain_data)

        static_data = {
            "raw_txn_account": common.RAW_TXN_ACCOUNT,
            "keyfile_pw": common.KEYFILE_PW,
        }
        config = merge(chain_data, static_data)
        pprint.pprint(config)
        write_config_json(config, datadir)

        shutil.make_archive(destination_dir, "zip", datadir)


def verify_chain_state(w3, chain_data):
    receipt = w3.eth.wait_for_transaction_receipt(chain_data["mined_txn_hash"])
    time.sleep(1)  # assert we mine a block in between (--dev.period=1)
    latest = w3.eth.get_block("latest")
    assert receipt.blockNumber <= latest.number


def mine_block(w3):
    origin_block_number = w3.eth.block_number

    start_time = time.time()
    while time.time() < start_time + 120:
        block_number = w3.eth.block_number
        if block_number > origin_block_number:
            return block_number
        else:
            time.sleep(0.1)
    else:
        raise Web3ValueError("No block mined during wait period")


def setup_chain_state(w3):
    coinbase = common.COINBASE

    #
    # Math Contract
    #
    math_contract_factory = w3.eth.contract(
        abi=MATH_CONTRACT_ABI,
        bytecode=MATH_CONTRACT_BYTECODE,
    )
    math_deploy_receipt = common.deploy_contract(w3, "math", math_contract_factory)
    assert is_dict(math_deploy_receipt)

    #
    # Emitter Contract
    #
    emitter_contract_factory = w3.eth.contract(
        abi=EMITTER_CONTRACT_ABI,
        bytecode=EMITTER_CONTRACT_BYTECODE,
    )
    emitter_deploy_receipt = common.deploy_contract(
        w3, "emitter", emitter_contract_factory
    )
    emitter_contract = emitter_contract_factory(
        emitter_deploy_receipt["contractAddress"]
    )

    txn_hash_with_log = emitter_contract.functions.logDouble(
        which=EMITTER_ENUM["LogDoubleWithIndex"],
        arg0=12345,
        arg1=54321,
    ).transact({"from": coinbase})
    print("TXN_HASH_WITH_LOG:", txn_hash_with_log)
    txn_receipt_with_log = w3.eth.wait_for_transaction_receipt(txn_hash_with_log)
    block_with_log = w3.eth.get_block(txn_receipt_with_log["blockHash"])
    print("BLOCK_HASH_WITH_LOG:", block_with_log["hash"])

    #
    # Revert Contract
    #
    revert_contract_factory = w3.eth.contract(
        abi=REVERT_CONTRACT_ABI,
        bytecode=REVERT_CONTRACT_BYTECODE,
    )
    revert_deploy_receipt = common.deploy_contract(
        w3, "revert", revert_contract_factory
    )
    revert_contract = revert_contract_factory(revert_deploy_receipt["contractAddress"])

    txn_hash_normal_function = revert_contract.functions.normalFunction().transact(
        {"gas": 320000, "from": coinbase}
    )
    print("TXN_HASH_REVERT_NORMAL:", txn_hash_normal_function)
    txn_hash_revert_with_msg = revert_contract.functions.revertWithMessage().transact(
        {"gas": 320000, "from": coinbase}
    )
    print("TXN_HASH_REVERT_WITH_MSG:", txn_hash_revert_with_msg)
    txn_receipt_revert_with_msg = w3.eth.wait_for_transaction_receipt(
        txn_hash_revert_with_msg
    )
    block_hash_revert_with_msg = w3.eth.get_block(
        txn_receipt_revert_with_msg["blockHash"]
    )
    print("BLOCK_HASH_REVERT_WITH_MSG:", block_hash_revert_with_msg["hash"])

    txn_hash_revert_with_no_msg = (
        revert_contract.functions.revertWithoutMessage().transact(
            {"gas": 320000, "from": coinbase}
        )
    )
    print("TXN_HASH_REVERT_WITH_NO_MSG:", txn_hash_revert_with_no_msg)
    txn_receipt_revert_with_no_msg = w3.eth.wait_for_transaction_receipt(
        txn_hash_revert_with_no_msg
    )
    block_hash_revert_no_msg = w3.eth.get_block(
        txn_receipt_revert_with_no_msg["blockHash"]
    )
    print("BLOCK_HASH_REVERT_NO_MSG:", block_hash_revert_no_msg["hash"])

    #
    # Offchain Lookup Contract
    #
    offchain_lookup_factory = w3.eth.contract(
        abi=OFFCHAIN_LOOKUP_ABI,
        bytecode=OFFCHAIN_LOOKUP_BYTECODE,
    )
    offchain_lookup_deploy_receipt = common.deploy_contract(
        w3, "offchain_lookup", offchain_lookup_factory
    )
    assert is_dict(offchain_lookup_deploy_receipt)

    #
    # Panic Errors Contract
    #
    panic_errors_contract_factory = w3.eth.contract(**PANIC_ERRORS_CONTRACT_DATA)
    panic_errors_deploy_receipt = common.deploy_contract(
        w3, "panic_errors", panic_errors_contract_factory
    )
    assert is_dict(panic_errors_deploy_receipt)

    #
    # Storage Contract
    #
    storage_contract_factory = w3.eth.contract(**STORAGE_CONTRACT_DATA)
    storage_contract_deploy_receipt = common.deploy_contract(
        w3, "storage_contract", storage_contract_factory
    )
    assert is_dict(storage_contract_deploy_receipt)

    #
    # Empty Block
    #
    time.sleep(2)
    empty_block_number = w3.eth.block_number
    print("MINED_EMPTY_BLOCK")
    empty_block = w3.eth.get_block(empty_block_number)
    assert is_dict(empty_block)
    assert not empty_block["transactions"]
    print("EMPTY_BLOCK_HASH:", empty_block["hash"])

    #
    # Block with Transaction
    #
    mined_txn_hash = w3.eth.send_transaction(
        {
            "from": coinbase,
            "to": coinbase,
            "value": 1,
            "gas": 21000,
            "gas_price": w3.eth.gas_price,
        }
    )
    mined_txn_receipt = w3.eth.wait_for_transaction_receipt(mined_txn_hash)
    print("MINED_TXN_HASH:", mined_txn_hash)
    block_with_txn = w3.eth.get_block(mined_txn_receipt["blockHash"])
    print("BLOCK_WITH_TXN_HASH:", block_with_txn["hash"])

    geth_fixture = {
        "keyfile_account_address": common.KEYFILE_ACCOUNT_ADDRESS,
        "keyfile_account_pkey": common.KEYFILE_ACCOUNT_PKEY,
        "math_deploy_txn_hash": math_deploy_receipt["transactionHash"],
        "math_address": math_deploy_receipt["contractAddress"],
        "emitter_deploy_txn_hash": emitter_deploy_receipt["transactionHash"],
        "emitter_address": emitter_deploy_receipt["contractAddress"],
        "offchain_lookup_address": offchain_lookup_deploy_receipt["contractAddress"],
        "panic_errors_contract_address": panic_errors_deploy_receipt["contractAddress"],
        "storage_contract_address": storage_contract_deploy_receipt["contractAddress"],
        "txn_hash_with_log": txn_hash_with_log,
        "block_hash_with_log": block_with_log["hash"],
        "empty_block_hash": empty_block["hash"],
        "mined_txn_hash": mined_txn_hash,
        "block_with_txn_hash": block_with_txn["hash"],
        "revert_address": revert_deploy_receipt["contractAddress"],
        "block_hash_revert_with_msg": block_hash_revert_with_msg["hash"],
        "block_hash_revert_no_msg": block_hash_revert_no_msg["hash"],
    }
    return geth_fixture


def update_geth_version_string(what_to_replace, new_version):
    for file_path, changes in what_to_replace.items():
        replaced = False
        with open(file_path) as file:
            lines = file.readlines()

            for i, line in enumerate(lines):
                for change in changes:
                    if change["line_to_replace"] in line:
                        lines[i] = change["replace_with"]
                        replaced = True
                        break

        if not replaced:
            raise ValueError(f"`geth_version` for {file_path} not found / replaced.")

        with open(file_path, "w") as file:
            file.writelines(lines)
        print(f"Updated geth_version in {file_path} to {new_version}")


def update_doc_version(new_version):
    changes = {
        "./docs/contributing.rst": [
            {
                "line_to_replace": "python -m geth.install ",
                "replace_with": f"      $ python -m geth.install v{new_version}\n",
            },
            {
                "line_to_replace": "GETH_BINARY=~",
                "replace_with": f"      $ GETH_BINARY=~/.py-geth/geth-v{new_version}/bin/geth uv run --group integration python -m scripts.generate_fixtures.go_ethereum\n",  # noqa: E501,
            },
        ]
    }

    update_geth_version_string(changes, new_version)


def update_fixture_generation_version(new_version):
    changes = {
        "./tests/integration/go_ethereum/conftest.py": [
            {
                "line_to_replace": "GETH_FIXTURE_ZIP = ",
                "replace_with": f'GETH_FIXTURE_ZIP = "geth-{new_version}-fixture.zip"\n',  # noqa: E501
            },
        ],
    }
    update_geth_version_string(changes, new_version)


def update_github_actions_geth_version(new_version):
    changes = {
        "./.github/workflows/test.yaml": [
            {
                "line_to_replace": "GETH_VERSION:",
                "replace_with": f'      GETH_VERSION: "{new_version}"\n',
            }
        ],
        "./.github/workflows/maintenance.yaml": [
            {
                "line_to_replace": "# geth-version",
                "replace_with": f'        default: "{new_version}"  # geth-version\n',
            }
        ],
    }
    update_geth_version_string(changes, new_version)


def remove_old_fixtures(current_geth_version):
    """
    Remove any geth fixture files that are not for the current version.
    """
    for file in os.listdir("./tests/integration"):
        if (
            file.startswith("geth-")
            and file.endswith("-fixture.zip")
            and current_geth_version not in file
        ):
            os.remove(os.path.join("./tests/integration", file))
            print(f"Removed old fixture: {file}")


if __name__ == "__main__":
    geth_binary = os.environ.get("GETH_BINARY", None)
    if not geth_binary:
        raise ValueError("GETH_BINARY not set. Cannot generate geth fixture.")

    geth_version = re.search(r"geth-v([\d.]+)/", geth_binary).group(1)
    generate_go_ethereum_fixture(f"./tests/integration/geth-{geth_version}-fixture")
    remove_old_fixtures(geth_version)
    update_github_actions_geth_version(geth_version)
    update_fixture_generation_version(geth_version)
    update_doc_version(geth_version)
