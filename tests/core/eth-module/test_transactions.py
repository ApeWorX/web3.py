import pytest
import collections
import itertools

from eth_account import (
    Account,
)
from eth_utils import (
    to_checksum_address,
    to_int,
)
from hexbytes import (
    HexBytes,
)
import pytest_asyncio

from tests.core.contracts.utils import (
    async_deploy,
    deploy,
)
from web3._utils.contract_sources.contract_data.math_contract import (
    MATH_CONTRACT_DATA,
)
from web3._utils.ens import (
    ens_addresses,
)
from web3._utils.rpc_abi import (
    RPC,
)
from web3.datastructures import (
    AttributeDict,
)
from web3.exceptions import (
    NameNotFound,
    TimeExhausted,
    TransactionNotFound,
    Web3ValidationError,
)

RECEIPT_TIMEOUT = 0.2


@pytest.fixture
def math_contract(w3):
    factory = w3.eth.contract(**MATH_CONTRACT_DATA)
    return deploy(w3, factory)


def _tx_indexing_response_iterator():
    while True:
        yield {"error": {"message": "transaction indexing in progress"}}
        yield {"error": {"message": "transaction indexing in progress"}}
        yield {"result": {"status": "0x1"}}


@pytest.mark.parametrize(
    "transaction",
    (
        {
            "gasPrice": 10**9,
            "accessList": (
                {
                    "address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "storageKeys": (
                        "0x0000000000000000000000000000000000000000000000000000000000000003",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000007",  # noqa: E501
                    ),
                },
                {
                    "address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
                    "storageKeys": (),
                },
            ),
        },
        {
            "maxFeePerGas": 10**9,
            "maxPriorityFeePerGas": 10**9,
            "accessList": (
                {
                    "address": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
                    "storageKeys": (
                        "0x0000000000000000000000000000000000000000000000000000000000000003",  # noqa: E501
                        "0x0000000000000000000000000000000000000000000000000000000000000007",  # noqa: E501
                    ),
                },
                {
                    "address": "0xbb9bc244d798123fde783fcc1c72d3bb8c189413",
                    "storageKeys": (),
                },
            ),
        },
    ),
    ids=[
        "storage_keys_access_list_txn",
        "storage_keys_dynamic_fee_txn",
    ],
)
def test_eth_tester_send_transaction_validation(w3, transaction):
    # Test that eth-tester transaction param validation does not
    # throw for properly formatted transactions.
    # This is especially important because we have key mapping differences
    # (camelCase to snake_case) mitigated by providers/eth-tester/middleware.
    txn_hash = w3.eth.send_transaction(transaction)
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=RECEIPT_TIMEOUT)
    assert receipt.get("blockNumber") is not None


@pytest.mark.parametrize(
    "make_chain_id, expect_success",
    (
        (
            lambda w3: w3.eth.chain_id,
            True,
        ),
        pytest.param(
            lambda w3: 999999999999,
            False,
        ),
    ),
)
def test_send_transaction_with_valid_chain_id(w3, make_chain_id, expect_success):
    transaction = {
        "to": w3.eth.accounts[1],
        "chainId": make_chain_id(w3),
    }
    if expect_success:
        txn_hash = w3.eth.send_transaction(transaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=RECEIPT_TIMEOUT)
        assert receipt.get("blockNumber") is not None
    else:
        with pytest.raises(Web3ValidationError) as exc_info:
            w3.eth.send_transaction(transaction)

        assert "chain ID" in str(exc_info.value)


@pytest.mark.parametrize(
    "to, _from",
    (
        (
            "registered-name-1.eth",
            "not-a-registered-name.eth",
        ),
        (
            "not-a-registered-name.eth",
            "registered-name-1.eth",
        ),
    ),
)
def test_send_transaction_with_invalid_ens_names(w3, to, _from):
    with ens_addresses(
        w3,
        [
            ("registered-name-1.eth", w3.eth.accounts[1]),
        ],
    ):
        transaction = {
            "to": to,
            "chainId": w3.eth.chain_id,
            "from": _from,
        }

        with pytest.raises(NameNotFound):
            w3.eth.send_transaction(transaction)


def test_send_transaction_with_ens_names(w3):
    with ens_addresses(
        w3,
        [
            ("registered-name-1.eth", w3.eth.accounts[1]),
            ("registered-name-2.eth", w3.eth.accounts[0]),
        ],
    ):
        transaction = {
            "to": "registered-name-1.eth",
            "chainId": w3.eth.chain_id,
            "from": "registered-name-2.eth",
        }

        txn_hash = w3.eth.send_transaction(transaction)
        receipt = w3.eth.wait_for_transaction_receipt(txn_hash, timeout=RECEIPT_TIMEOUT)
        assert receipt.get("blockNumber") is not None


def test_wait_for_missing_receipt(w3):
    with pytest.raises(TimeExhausted):
        w3.eth.wait_for_transaction_receipt(b"\0" * 32, timeout=RECEIPT_TIMEOUT)


def test_passing_string_to_to_hex(w3):
    with pytest.raises(TimeExhausted):
        transaction_hash = (
            "0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060"
        )
        w3.eth.wait_for_transaction_receipt(transaction_hash, timeout=RECEIPT_TIMEOUT)


def test_unmined_transaction_wait_for_receipt(w3, request_mocker):
    receipt_counters = collections.defaultdict(itertools.count)

    txn_hash = w3.eth.send_transaction(
        {
            "from": w3.eth.default_account,
            "to": "0xd3CdA913deB6f67967B99D67aCDFa1712C293601",
            "value": 123457,
        }
    )
    unmocked_make_request = w3.provider.make_request

    with request_mocker(
        w3,
        mock_results={
            RPC.eth_getTransactionReceipt: lambda method, params: (
                None
                if next(receipt_counters[params[0]]) < 5
                else unmocked_make_request(method, params)["result"]
            )
        },
    ):
        with pytest.raises(TransactionNotFound):
            w3.eth.get_transaction_receipt(txn_hash)

        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        assert txn_receipt["transactionHash"] == txn_hash
        assert txn_receipt["blockHash"] is not None


def test_eth_wait_for_transaction_receipt_transaction_indexing_in_progress(
    w3, request_mocker
):
    i = _tx_indexing_response_iterator()
    with request_mocker(
        w3,
        mock_responses={"eth_getTransactionReceipt": lambda *_: next(i)},
    ):
        receipt = w3.eth.wait_for_transaction_receipt(f"0x{'00' * 32}")
        assert receipt == {"status": 1}


def test_get_transaction_formatters(w3, request_mocker):
    non_checksummed_addr = "0xB2930B35844A230F00E51431ACAE96FE543A0347"  # all uppercase
    unformatted_transaction = {
        "blobVersionedHashes": [
            "0x01b8c5b09810b5fc07355d3da42e2c3a3e200c1d9a678491b7e8e256fc50cc4f",
            "0x015b4c8cc4f86aa2d2cf9e9ce97fca704a11a6c20f6b1d6c00a6e15f6d60a6df",
            "0x01878f80eaf10be1a6f618e6f8c071b10a6c14d9b89a3bf2a3f3cf2db6c5681d",
        ],
        "blockHash": (
            "0x849044202a39ae36888481f90d62c3826bca8269c2716d7a38696b4f45e61d83"
        ),
        "blockNumber": "0x1b4",
        "transactionIndex": "0x0",
        "nonce": "0x0",
        "gas": "0x4c4b40",
        "gasPrice": "0x1",
        "maxFeePerBlobGas": "0x1",
        "maxFeePerGas": "0x1",
        "maxPriorityFeePerGas": "0x1",
        "value": "0x1",
        "from": non_checksummed_addr,
        "publicKey": "0x",
        "r": "0xd148ae70c8cbef3a038e70e6d1639f0951e60a2965820f33bad19d0a6c2b8116",
        "raw": "0x142ab034696c09dcfb2a8b086b494f3f4c419e67b6c04d95882f87156a3b6f35",
        "s": "0x6f5216fc207221a11efe2e4c3e3a881a0b5ca286ede538fc9dbc403b2009ea76",
        "to": non_checksummed_addr,
        "hash": "0x142ab034696c09dcfb2a8b086b494f3f4c419e67b6c04d95882f87156a3b6f35",
        "v": "0x1",
        "yParity": "0x1",
        "standardV": "0x1",
        "type": "0x2",
        "chainId": "0x539",
        "accessList": [
            {
                "address": non_checksummed_addr,
                "storageKeys": [
                    "0x0000000000000000000000000000000000000000000000000000000000000032",  # noqa: E501
                    "0x0000000000000000000000000000000000000000000000000000000000000036",  # noqa: E501
                ],
            },
            {
                "address": non_checksummed_addr,
                "storageKeys": [],
            },
        ],
        "input": "0x5b34b966",
    }

    with request_mocker(
        w3, mock_results={RPC.eth_getTransactionByHash: unformatted_transaction}
    ):
        # test against eth_getTransactionByHash
        received_tx = w3.eth.get_transaction("")

    checksummed_addr = to_checksum_address(non_checksummed_addr)
    assert non_checksummed_addr != checksummed_addr

    expected = AttributeDict(
        {
            "blobVersionedHashes": [
                HexBytes(
                    "0x01b8c5b09810b5fc07355d3da42e2c3a3e200c1d9a678491b7e8e256fc50cc4f"
                ),
                HexBytes(
                    "0x015b4c8cc4f86aa2d2cf9e9ce97fca704a11a6c20f6b1d6c00a6e15f6d60a6df"
                ),
                HexBytes(
                    "0x01878f80eaf10be1a6f618e6f8c071b10a6c14d9b89a3bf2a3f3cf2db6c5681d"
                ),
            ],
            "blockHash": HexBytes(unformatted_transaction["blockHash"]),
            "blockNumber": to_int(hexstr=unformatted_transaction["blockNumber"]),
            "transactionIndex": 0,
            "nonce": 0,
            "gas": to_int(hexstr=unformatted_transaction["gas"]),
            "gasPrice": 1,
            "maxFeePerBlobGas": 1,
            "maxFeePerGas": 1,
            "maxPriorityFeePerGas": 1,
            "value": 1,
            "from": checksummed_addr,
            "publicKey": HexBytes(unformatted_transaction["publicKey"]),
            "r": HexBytes(unformatted_transaction["r"]),
            "raw": HexBytes(unformatted_transaction["raw"]),
            "s": HexBytes(unformatted_transaction["s"]),
            "to": to_checksum_address(non_checksummed_addr),
            "hash": HexBytes(unformatted_transaction["hash"]),
            "v": 1,
            "yParity": 1,
            "standardV": 1,
            "type": 2,
            "chainId": 1337,
            "accessList": [
                AttributeDict(
                    {
                        "address": checksummed_addr,
                        "storageKeys": [
                            "0x0000000000000000000000000000000000000000000000000000000000000032",  # noqa: E501
                            "0x0000000000000000000000000000000000000000000000000000000000000036",  # noqa: E501
                        ],
                    }
                ),
                AttributeDict(
                    {
                        "address": checksummed_addr,
                        "storageKeys": [],
                    }
                ),
            ],
            "input": HexBytes(unformatted_transaction["input"]),
        }
    )

    assert received_tx == expected


def test_eth_send_raw_blob_transaction(w3):
    # `eth-tester` account #1's pkey is "0x00000000...01"
    acct = w3.eth.account.from_key(f"0x{'00' * 31}01")

    text = "We are the music makers and we are the dreamers of dreams."
    encoded_text = w3.codec.encode(["string"], [text])
    # Blobs contain 4096 32-byte field elements. Subtract the length of the encoded text
    # divided into 32-byte chunks from 4096 and pad the rest with zeros.
    blob_data = (b"\x00" * 32 * (4096 - len(encoded_text) // 32)) + encoded_text

    tx = {
        "type": 3,
        "chainId": 1337,
        "from": acct.address,
        "to": "0xb45BEc6eeCA2a09f4689Dd308F550Ad7855051B5",
        "value": 0,
        "gas": 21000,
        "maxFeePerGas": 10**10,
        "maxPriorityFeePerGas": 10**10,
        "maxFeePerBlobGas": 10**10,
        "nonce": w3.eth.get_transaction_count(acct.address),
    }

    signed = acct.sign_transaction(tx, blobs=[blob_data])

    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    transaction = w3.eth.get_transaction(tx_hash)

    assert len(transaction["blobVersionedHashes"]) == 1
    assert transaction["blobVersionedHashes"][0] == HexBytes(
        "0x0127c38bcad458d932e828b580b9ad97310be01407dfa0ed88118735980a3e9a"
    )


def test_send_set_code_transaction(w3, math_contract):
    pkey = w3.provider.ethereum_tester.backend.account_keys[0]
    acct = Account.from_key(pkey)

    nonce = w3.eth.get_transaction_count(acct.address)
    chain_id = w3.eth.chain_id

    auth = {
        "chainId": chain_id,
        "address": math_contract.address,
        "nonce": nonce + 1,
    }
    signed_auth = acct.sign_authorization(auth)

    # get current math counter and increase it only in the delegation by n
    math_counter = math_contract.functions.counter().call()
    built_tx = math_contract.functions.incrementCounter(
        math_counter + 1337
    ).build_transaction({})
    txn = {
        "chainId": chain_id,
        "to": acct.address,
        "value": 0,
        "gas": 200_000,
        "nonce": nonce,
        "maxPriorityFeePerGas": 10**9,
        "maxFeePerGas": 10**9,
        "data": built_tx["data"],
        "authorizationList": [signed_auth],
    }

    tx_hash = w3.eth.send_transaction(txn)
    get_tx = w3.eth.get_transaction(tx_hash)
    w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)

    code = w3.eth.get_code(acct.address)

    assert code.to_0x_hex().lower() == f"0xef0100{math_contract.address[2:].lower()}"
    delegated = w3.eth.contract(address=acct.address, abi=math_contract.abi)
    # assert the math counter is increased by 1337 only in delegated acct
    assert math_contract.functions.counter().call() == math_counter
    delegated_call = delegated.functions.counter().call()
    assert delegated_call == math_counter + 1337

    assert len(get_tx["authorizationList"]) == 1
    get_auth = get_tx["authorizationList"][0]
    assert get_auth["chainId"] == chain_id
    assert get_auth["address"].lower() == math_contract.address.lower()
    assert get_auth["nonce"] == nonce + 1
    assert isinstance(get_auth["yParity"], int)
    assert isinstance(get_auth["r"], int)
    assert isinstance(get_auth["s"], int)

    # reset code
    reset_auth = {
        "chainId": chain_id,
        "address": "0x" + ("00" * 20),
        "nonce": nonce + 3,
    }
    signed_reset_auth = acct.sign_authorization(reset_auth)
    new_txn = dict(txn)
    new_txn["authorizationList"] = [signed_reset_auth]
    new_txn["nonce"] = nonce + 2

    reset_tx_hash = w3.eth.send_transaction(new_txn)
    w3.eth.wait_for_transaction_receipt(reset_tx_hash, timeout=10)

    reset_code = w3.eth.get_code(acct.address)
    assert reset_code == HexBytes("0x")


# --- async --- #


@pytest_asyncio.fixture
async def async_math_contract(async_w3):
    factory = async_w3.eth.contract(**MATH_CONTRACT_DATA)
    return await async_deploy(async_w3, factory)


@pytest.mark.asyncio
async def test_async_wait_for_transaction_receipt_transaction_indexing_in_progress(
    async_w3, request_mocker
):
    i = _tx_indexing_response_iterator()
    async with request_mocker(
        async_w3,
        mock_responses={"eth_getTransactionReceipt": lambda *_: next(i)},
    ):
        receipt = await async_w3.eth.wait_for_transaction_receipt(f"0x{'00' * 32}")
        assert receipt == {"status": 1}


@pytest.mark.asyncio
async def test_async_send_raw_blob_transaction(async_w3):
    # `eth-tester` account #1's pkey is "0x00000000...01"
    acct = async_w3.eth.account.from_key(f"0x{'00' * 31}01")

    text = "We are the music makers and we are the dreamers of dreams."
    encoded_text = async_w3.codec.encode(["string"], [text])
    # Blobs contain 4096 32-byte field elements. Subtract the length of the encoded text
    # divided into 32-byte chunks from 4096 and pad the rest with zeros.
    blob_data = (b"\x00" * 32 * (4096 - len(encoded_text) // 32)) + encoded_text

    tx = {
        "type": 3,
        "chainId": 1337,
        "from": acct.address,
        "to": "0xb45BEc6eeCA2a09f4689Dd308F550Ad7855051B5",
        "value": 0,
        "gas": 21000,
        "maxFeePerGas": 10**10,
        "maxPriorityFeePerGas": 10**10,
        "maxFeePerBlobGas": 10**10,
        "nonce": await async_w3.eth.get_transaction_count(acct.address),
    }

    signed = acct.sign_transaction(tx, blobs=[blob_data])

    tx_hash = await async_w3.eth.send_raw_transaction(signed.raw_transaction)
    transaction = await async_w3.eth.get_transaction(tx_hash)

    assert len(transaction["blobVersionedHashes"]) == 1
    assert transaction["blobVersionedHashes"][0] == HexBytes(
        "0x0127c38bcad458d932e828b580b9ad97310be01407dfa0ed88118735980a3e9a"
    )


@pytest.mark.asyncio
async def test_async_send_set_code_transaction(async_w3, async_math_contract):
    pkey = async_w3.provider.ethereum_tester.backend.account_keys[0]
    acct = Account.from_key(pkey)

    nonce = await async_w3.eth.get_transaction_count(acct.address)
    chain_id = await async_w3.eth.chain_id

    auth = {
        "chainId": chain_id,
        "address": async_math_contract.address,
        "nonce": nonce + 1,
    }
    signed_auth = acct.sign_authorization(auth)

    # get current math counter and increase it only in the delegation by n
    math_counter = await async_math_contract.functions.counter().call()
    built_tx = await async_math_contract.functions.incrementCounter(
        math_counter + 1337
    ).build_transaction({})
    txn = {
        "chainId": chain_id,
        "to": acct.address,
        "value": 0,
        "gas": 200_000,
        "nonce": nonce,
        "maxPriorityFeePerGas": 10**9,
        "maxFeePerGas": 10**9,
        "data": built_tx["data"],
        "authorizationList": [signed_auth],
    }

    tx_hash = await async_w3.eth.send_transaction(txn)
    get_tx = await async_w3.eth.get_transaction(tx_hash)
    await async_w3.eth.wait_for_transaction_receipt(tx_hash, timeout=10)

    code = await async_w3.eth.get_code(acct.address)

    assert (
        code.to_0x_hex().lower() == f"0xef0100{async_math_contract.address[2:].lower()}"
    )
    delegated = async_w3.eth.contract(address=acct.address, abi=async_math_contract.abi)
    # assert the math counter is increased by 1337 only in delegated acct
    assert await async_math_contract.functions.counter().call() == math_counter
    delegated_call = await delegated.functions.counter().call()
    assert delegated_call == math_counter + 1337

    assert len(get_tx["authorizationList"]) == 1
    get_auth = get_tx["authorizationList"][0]
    assert get_auth["chainId"] == chain_id
    assert get_auth["address"].lower() == async_math_contract.address.lower()
    assert get_auth["nonce"] == nonce + 1
    assert isinstance(get_auth["yParity"], int)
    assert isinstance(get_auth["r"], int)
    assert isinstance(get_auth["s"], int)

    # reset code
    reset_auth = {
        "chainId": chain_id,
        "address": "0x" + ("00" * 20),
        "nonce": nonce + 3,
    }
    signed_reset_auth = acct.sign_authorization(reset_auth)
    new_txn = dict(txn)
    new_txn["authorizationList"] = [signed_reset_auth]
    new_txn["nonce"] = nonce + 2

    reset_tx_hash = await async_w3.eth.send_transaction(new_txn)
    await async_w3.eth.wait_for_transaction_receipt(reset_tx_hash, timeout=10)

    reset_code = await async_w3.eth.get_code(acct.address)
    assert reset_code == HexBytes("0x")
