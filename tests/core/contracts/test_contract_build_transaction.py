import pytest

from eth_utils.toolz import (
    dissoc,
)

from web3.exceptions import (
    Web3ValidationError,
    Web3ValueError,
)
from web3.gas_strategies.time_based import (
    fast_gas_price_strategy,
)


def test_build_transaction_not_paying_to_nonpayable_function(
    w3, payable_tester_contract, build_transaction
):
    txn = build_transaction(
        contract=payable_tester_contract, contract_function="doNoValueCall"
    )
    assert dissoc(txn, "gas") == {
        "to": payable_tester_contract.address,
        "data": "0xe4cb8f5c",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


def test_build_transaction_paying_to_nonpayable_function(
    w3, payable_tester_contract, build_transaction
):
    with pytest.raises(Web3ValidationError):
        build_transaction(
            contract=payable_tester_contract,
            contract_function="doNoValueCall",
            tx_params={"value": 1},
        )


def test_build_transaction_with_contract_no_arguments(
    w3, math_contract, build_transaction
):
    txn = build_transaction(
        contract=math_contract, contract_function="incrementCounter"
    )
    assert dissoc(txn, "gas") == {
        "to": math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


def test_build_transaction_with_contract_no_arguments_no_parens(
    w3, math_contract, build_transaction
):
    txn = math_contract.functions.incrementCounter.build_transaction()
    assert dissoc(txn, "gas") == {
        "to": math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


def test_build_transaction_with_contract_fallback_function(
    w3, fallback_function_contract
):
    txn = fallback_function_contract.fallback.build_transaction()
    assert dissoc(txn, "gas") == {
        "to": fallback_function_contract.address,
        "data": "0x",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


def test_build_transaction_with_contract_class_method(
    w3, math_contract_factory, math_contract, build_transaction
):
    txn = build_transaction(
        contract=math_contract_factory,
        contract_function="incrementCounter",
        tx_params={"to": math_contract.address},
    )
    assert dissoc(txn, "gas") == {
        "to": math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


def test_build_transaction_with_contract_default_account_is_set(
    w3, math_contract, build_transaction
):
    txn = build_transaction(
        contract=math_contract, contract_function="incrementCounter"
    )
    assert dissoc(txn, "gas") == {
        "to": math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


def test_build_transaction_with_gas_price_strategy_set(
    w3, math_contract, build_transaction
):
    def my_gas_price_strategy(w3, transaction_params):
        return 5

    w3.eth.set_gas_price_strategy(my_gas_price_strategy)
    txn = build_transaction(
        contract=math_contract, contract_function="incrementCounter"
    )
    assert dissoc(txn, "gas") == {
        "to": math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "gasPrice": 5,
        "chainId": 131277322940537,
    }


def test_build_transaction_with_contract_data_supplied_errors(
    w3, math_contract, build_transaction
):
    with pytest.raises(Web3ValueError):
        build_transaction(
            contract=math_contract,
            contract_function="incrementCounter",
            tx_params={"data": "0x000"},
        )


def test_build_transaction_with_contract_to_address_supplied_errors(
    w3, math_contract, build_transaction
):
    with pytest.raises(Web3ValueError):
        build_transaction(
            contract=math_contract,
            contract_function="incrementCounter",
            tx_params={"to": "0xb2930B35844a230f00E51431aCAe96Fe543a0347"},
        )


@pytest.mark.parametrize(
    "transaction_args,method_args,method_kwargs,expected,skip_testrpc",
    (
        (
            {},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "chainId": 131277322940537,
            },
            False,
        ),
        (
            {"gas": 800000},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "chainId": 131277322940537,
            },
            False,
        ),
        (  # legacy transaction, explicit gasPrice
            {"gasPrice": 22**8},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "gasPrice": 22**8,
                "chainId": 131277322940537,
            },
            False,
        ),
        (
            {"maxFeePerGas": 22**8, "maxPriorityFeePerGas": 22**8},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 22**8,
                "maxPriorityFeePerGas": 22**8,
                "chainId": 131277322940537,
            },
            False,
        ),
        (
            {"nonce": 7},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "nonce": 7,
                "chainId": 131277322940537,
            },
            True,
        ),
        (
            {"value": 20000},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 20000,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "chainId": 131277322940537,
            },
            False,
        ),
    ),
    ids=[
        "Standard",
        "Explicit Gas",
        "Explicit Gas Price",
        "Explicit Dynamic Fees",
        "Explicit Nonce",
        "With Value",
    ],
)
def test_build_transaction_with_contract_arguments(
    w3,
    skip_if_testrpc,
    math_contract,
    transaction_args,
    method_args,
    method_kwargs,
    expected,
    skip_testrpc,
    build_transaction,
):
    if skip_testrpc:
        skip_if_testrpc(w3)

    txn = build_transaction(
        contract=math_contract,
        contract_function="incrementCounter",
        func_args=method_args,
        func_kwargs=method_kwargs,
        tx_params=transaction_args,
    )
    expected["to"] = math_contract.address
    assert txn is not None
    if "gas" in transaction_args:
        assert txn["gas"] == transaction_args["gas"]
    else:
        assert "gas" in txn
    assert dissoc(txn, "gas") == expected


@pytest.mark.asyncio
async def test_async_build_transaction_not_paying_to_nonpayable_function(
    async_w3, async_payable_tester_contract, async_build_transaction
):
    txn = await async_build_transaction(
        contract=async_payable_tester_contract, contract_function="doNoValueCall"
    )
    assert dissoc(txn, "gas") == {
        "to": async_payable_tester_contract.address,
        "data": "0xe4cb8f5c",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_paying_to_nonpayable_function(
    async_w3, async_payable_tester_contract, async_build_transaction
):
    with pytest.raises(Web3ValidationError):
        await async_build_transaction(
            contract=async_payable_tester_contract,
            contract_function="doNoValueCall",
            tx_params={"value": 1},
        )


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_no_arguments(
    async_w3, async_math_contract, async_build_transaction
):
    txn = await async_build_transaction(
        contract=async_math_contract, contract_function="incrementCounter"
    )
    assert dissoc(txn, "gas") == {
        "to": async_math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_no_arguments_no_parens(
    async_w3, async_math_contract, async_build_transaction
):
    txn = await async_math_contract.functions.incrementCounter.build_transaction()
    assert dissoc(txn, "gas") == {
        "to": async_math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_fallback_function(
    async_w3, async_fallback_function_contract
):
    txn = await async_fallback_function_contract.fallback.build_transaction()
    assert dissoc(txn, "gas") == {
        "to": async_fallback_function_contract.address,
        "data": "0x",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_class_method(
    async_w3,
    async_math_contract_factory,
    async_math_contract,
    async_build_transaction,
):
    txn = await async_build_transaction(
        contract=async_math_contract_factory,
        contract_function="incrementCounter",
        tx_params={"to": async_math_contract.address},
    )
    assert dissoc(txn, "gas") == {
        "to": async_math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_default_account_is_set(
    async_w3, async_math_contract, async_build_transaction
):
    txn = await async_build_transaction(
        contract=async_math_contract, contract_function="incrementCounter"
    )
    assert dissoc(txn, "gas") == {
        "to": async_math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "maxFeePerGas": 2750000000,
        "maxPriorityFeePerGas": 10**9,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_with_gas_price_strategy_set(
    async_w3, async_math_contract, async_build_transaction
):
    def my_gas_price_strategy(async_w3, transaction_params):
        return 5

    async_w3.eth.set_gas_price_strategy(my_gas_price_strategy)
    txn = await async_build_transaction(
        contract=async_math_contract, contract_function="incrementCounter"
    )
    assert dissoc(txn, "gas") == {
        "to": async_math_contract.address,
        "data": "0x5b34b966",
        "value": 0,
        "gasPrice": 5,
        "chainId": 131277322940537,
    }


@pytest.mark.asyncio
async def test_async_build_transaction_with_fast_gas_price_strategy(
    async_w3, async_math_contract, async_build_transaction, request_mocker
):
    async_w3.eth.set_gas_price_strategy(fast_gas_price_strategy)

    async with request_mocker(
        async_w3,
        mock_results={
            "eth_getBlockByNumber": {
                "hash": "0x" + "00" * 32,
                "number": 0,
                "parentHash": None,
                "transactions": [],
                "miner": "0x" + "AA" * 20,
                "timestamp": 0,
            }
        },
    ):
        txn = await async_build_transaction(
            contract=async_math_contract, contract_function="incrementCounter"
        )

    assert isinstance(txn["gasPrice"], int)


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_data_supplied_errors(
    async_w3, async_math_contract, async_build_transaction
):
    with pytest.raises(Web3ValueError):
        await async_build_transaction(
            contract=async_math_contract,
            contract_function="incrementCounter",
            tx_params={"data": "0x000"},
        )


@pytest.mark.asyncio
async def test_async_build_transaction_with_contract_to_address_supplied_errors(
    async_w3, async_math_contract, async_build_transaction
):
    with pytest.raises(Web3ValueError):
        await async_build_transaction(
            contract=async_math_contract,
            contract_function="incrementCounter",
            tx_params={"to": "0xb2930B35844a230f00E51431aCAe96Fe543a0347"},
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "transaction_args,method_args,method_kwargs,expected,skip_testrpc",
    (
        (
            {},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "chainId": 131277322940537,
            },
            False,
        ),
        (
            {"gas": 800000},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "chainId": 131277322940537,
            },
            False,
        ),
        (  # legacy transaction, explicit gasPrice
            {"gasPrice": 22**8},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "gasPrice": 22**8,
                "chainId": 131277322940537,
            },
            False,
        ),
        (
            {"maxFeePerGas": 22**8, "maxPriorityFeePerGas": 22**8},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 22**8,
                "maxPriorityFeePerGas": 22**8,
                "chainId": 131277322940537,
            },
            False,
        ),
        (
            {"nonce": 7},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 0,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "nonce": 7,
                "chainId": 131277322940537,
            },
            True,
        ),
        (
            {"value": 20000},
            (5,),
            {},
            {
                "data": "0x6abbb3b40000000000000000000000000000000000000000000000000000000000000005",  # noqa: E501
                "value": 20000,
                "maxFeePerGas": 2750000000,
                "maxPriorityFeePerGas": 1000000000,
                "chainId": 131277322940537,
            },
            False,
        ),
    ),
    ids=[
        "Standard",
        "Explicit Gas",
        "Explicit Gas Price",
        "Explicit Dynamic Fees",
        "Explicit Nonce",
        "With Value",
    ],
)
async def test_async_build_transaction_with_contract_with_arguments(
    async_w3,
    async_skip_if_testrpc,
    async_math_contract,
    transaction_args,
    method_args,
    method_kwargs,
    expected,
    skip_testrpc,
    async_build_transaction,
):
    if skip_testrpc:
        async_skip_if_testrpc(async_w3)

    txn = await async_build_transaction(
        contract=async_math_contract,
        contract_function="incrementCounter",
        func_args=method_args,
        func_kwargs=method_kwargs,
        tx_params=transaction_args,
    )
    expected["to"] = async_math_contract.address
    assert txn is not None
    if "gas" in transaction_args:
        assert txn["gas"] == transaction_args["gas"]
    else:
        assert "gas" in txn
    assert dissoc(txn, "gas") == expected
