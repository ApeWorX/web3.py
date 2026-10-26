import pytest
import random

from eth_utils import (
    to_tuple,
)


@to_tuple
def deploy_contracts(w3, contract, wait_for_transaction):
    for _ in range(25):
        tx_hash = contract.constructor().transact()
        wait_for_transaction(w3, tx_hash)
        yield w3.eth.get_transaction_receipt(tx_hash)["contractAddress"]


def pad_with_transactions(w3):
    accounts = w3.eth.accounts
    for tx_count in range(random.randint(0, 10)):
        _from = accounts[random.randint(0, len(accounts) - 1)]
        _to = accounts[random.randint(0, len(accounts) - 1)]
        value = 50 + tx_count
        w3.eth.send_transaction({"from": _from, "to": _to, "value": value})


def single_transaction(w3):
    accounts = w3.eth.accounts
    _from = accounts[random.randint(0, len(accounts) - 1)]
    _to = accounts[random.randint(0, len(accounts) - 1)]
    value = 50
    tx_hash = w3.eth.send_transaction({"from": _from, "to": _to, "value": value})
    return tx_hash


@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
def test_event_filter_new_events(
    w3,
    emitter,
    emitter_contract_factory,
    wait_for_transaction,
    emitter_contract_event_ids,
    api_style,
    create_filter,
):
    matching_transact = emitter.functions.logNoArgs(which=1).transact
    non_matching_transact = emitter.functions.logNoArgs(which=0).transact

    if api_style == "build_filter":
        builder = emitter.events.LogNoArguments.build_filter()
        builder.from_block = "latest"
        event_filter = builder.deploy(w3)
    else:
        event_filter = emitter.events.LogNoArguments.create_filter(from_block="latest")

    expected_match_counter = 0

    while w3.eth.block_number < 50:
        is_match = bool(random.randint(0, 1))
        if is_match:
            expected_match_counter += 1
            wait_for_transaction(w3, matching_transact())
            pad_with_transactions(w3)
            continue
        non_matching_transact()
        pad_with_transactions(w3)

    assert len(event_filter.get_new_entries()) == expected_match_counter


def test_block_filter(w3):
    block_filter = w3.eth.filter("latest")
    while w3.eth.block_number < 50:
        pad_with_transactions(w3)

    assert len(block_filter.get_new_entries()) == w3.eth.block_number


@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
def test_event_filter_new_events_many_deployed_contracts(
    w3,
    emitter,
    emitter_contract_factory,
    wait_for_transaction,
    emitter_contract_event_ids,
    api_style,
    create_filter,
):
    matching_transact = emitter.functions.logNoArgs(which=1).transact

    deployed_contract_addresses = deploy_contracts(
        w3, emitter_contract_factory, wait_for_transaction
    )

    def gen_non_matching_transact():
        while True:
            contract_address = deployed_contract_addresses[
                random.randint(0, len(deployed_contract_addresses) - 1)
            ]
            yield (
                w3.eth.contract(
                    address=contract_address, abi=emitter_contract_factory.abi
                )
                .functions.logNoArgs(which=1)
                .transact
            )

    non_matching_transact = gen_non_matching_transact()

    if api_style == "build_filter":
        builder = emitter.events.LogNoArguments.build_filter()
        builder.from_block = "latest"
        event_filter = builder.deploy(w3)
    else:
        event_filter = emitter.events.LogNoArguments.create_filter(from_block="latest")

    expected_match_counter = 0

    while w3.eth.block_number < 50:
        is_match = bool(random.randint(0, 1))
        if is_match:
            expected_match_counter += 1
            matching_transact()
            pad_with_transactions(w3)
            continue
        next(non_matching_transact)()
        pad_with_transactions(w3)

    assert len(event_filter.get_new_entries()) == expected_match_counter


# --- async --- #


async def async_deploy_contracts(async_w3, contract, async_wait_for_transaction):
    txs = []
    for _ in range(25):
        tx_hash = await contract.constructor().transact()
        await async_wait_for_transaction(async_w3, tx_hash)
        tx = await async_w3.eth.get_transaction_receipt(tx_hash)

        txs.append(tx["contractAddress"])

    return tuple(txs)


async def async_pad_with_transactions(async_w3):
    accounts = await async_w3.eth.accounts
    for tx_count in range(random.randint(0, 10)):
        _from = accounts[random.randint(0, len(accounts) - 1)]
        _to = accounts[random.randint(0, len(accounts) - 1)]
        value = 50 + tx_count
        await async_w3.eth.send_transaction({"from": _from, "to": _to, "value": value})


async def async_single_transaction(async_w3):
    accounts = await async_w3.eth.accounts
    _from = accounts[random.randint(0, len(accounts) - 1)]
    _to = accounts[random.randint(0, len(accounts) - 1)]
    value = 50
    tx_hash = await async_w3.eth.send_transaction(
        {"from": _from, "to": _to, "value": value}
    )
    return tx_hash


@pytest.mark.asyncio
@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
async def test_async_event_filter_new_events(
    async_w3,
    async_emitter,
    async_wait_for_transaction,
    api_style,
):
    matching_transact = async_emitter.functions.logNoArgs(which=1).transact
    non_matching_transact = async_emitter.functions.logNoArgs(which=0).transact

    if api_style == "build_filter":
        builder = async_emitter.events.LogNoArguments.build_filter()
        builder.from_block = "latest"
        event_filter = await builder.deploy(async_w3)
    else:
        event_filter = await async_emitter.events.LogNoArguments.create_filter(
            from_block="latest"
        )

    expected_match_counter = 0

    eth_block_number = await async_w3.eth.block_number
    while eth_block_number < 50:
        is_match = bool(random.randint(0, 1))
        if is_match:
            expected_match_counter += 1
            awaited_matching_transact = await matching_transact()
            await async_wait_for_transaction(async_w3, awaited_matching_transact)
            await async_pad_with_transactions(async_w3)
            continue
        await non_matching_transact()
        await async_pad_with_transactions(async_w3)
        eth_block_number = await async_w3.eth.block_number

    new_entries = await event_filter.get_new_entries()
    assert len(new_entries) == expected_match_counter


@pytest.mark.asyncio
async def test_async_block_filter(async_w3):
    block_filter = await async_w3.eth.filter("latest")

    eth_block_number = await async_w3.eth.block_number
    while eth_block_number < 50:
        await async_pad_with_transactions(async_w3)
        eth_block_number = await async_w3.eth.block_number

    new_entries = await block_filter.get_new_entries()
    eth_block_number = await async_w3.eth.block_number
    assert len(new_entries) == eth_block_number


@pytest.mark.asyncio
@pytest.mark.parametrize("api_style", ("v4", "build_filter"))
async def test_async_event_filter_new_events_many_deployed_contracts(
    async_w3,
    async_emitter,
    async_emitter_contract_factory,
    async_wait_for_transaction,
    api_style,
):
    matching_transact = async_emitter.functions.logNoArgs(which=1).transact

    deployed_contract_addresses = await async_deploy_contracts(
        async_w3, async_emitter_contract_factory, async_wait_for_transaction
    )

    async def gen_non_matching_transact():
        while True:
            contract_address = deployed_contract_addresses[
                random.randint(0, len(deployed_contract_addresses) - 1)
            ]
            yield (
                async_w3.eth.contract(
                    address=contract_address, abi=async_emitter_contract_factory.abi
                )
                .functions.logNoArgs(which=1)
                .transact
            )

    non_matching_transact = gen_non_matching_transact()

    if api_style == "build_filter":
        builder = async_emitter.events.LogNoArguments.build_filter()
        builder.from_block = "latest"
        event_filter = await builder.deploy(async_w3)
    else:
        event_filter = await async_emitter.events.LogNoArguments.create_filter(
            from_block="latest"
        )

    expected_match_counter = 0

    eth_block_number = await async_w3.eth.block_number
    while eth_block_number < 50:
        is_match = bool(random.randint(0, 1))
        if is_match:
            expected_match_counter += 1
            await matching_transact()
            await async_pad_with_transactions(async_w3)
            continue
        await non_matching_transact.__anext__()
        await async_pad_with_transactions(async_w3)
        eth_block_number = await async_w3.eth.block_number

    new_entries = await event_filter.get_new_entries()
    assert len(new_entries) == expected_match_counter
