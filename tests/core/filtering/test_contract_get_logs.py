import pytest

from web3._utils.contract_sources.contract_data._custom_contract_data import (
    EMITTER_ENUM,
)
from web3.exceptions import (
    Web3ValidationError,
)


def test_contract_get_available_events(
    emitter,
):
    """We can iterate over available contract events"""
    contract = emitter
    events = list(contract.events)
    assert len(events) == len(EMITTER_ENUM)


def test_contract_get_logs_all(
    w3,
    emitter,
    wait_for_transaction,
    emitter_contract_event_ids,
):
    contract = emitter
    event_id = emitter_contract_event_ids.LogNoArguments

    txn_hash = contract.functions.logNoArgs(event_id).transact()
    wait_for_transaction(w3, txn_hash)

    log_entries = list(contract.events.LogNoArguments.get_logs())
    assert len(log_entries) == 1
    assert log_entries[0]["transactionHash"] == txn_hash


def test_contract_get_logs_range(
    w3,
    emitter,
    wait_for_transaction,
    emitter_contract_event_ids,
):
    contract = emitter
    event_id = emitter_contract_event_ids.LogNoArguments

    assert w3.eth.block_number == 2
    txn_hash = contract.functions.logNoArgs(event_id).transact()
    # Mined as block 3
    wait_for_transaction(w3, txn_hash)
    assert w3.eth.block_number == 3

    log_entries = list(contract.events.LogNoArguments.get_logs())
    assert len(log_entries) == 1

    log_entries = list(
        contract.events.LogNoArguments.get_logs(from_block=2, to_block=3)
    )
    assert len(log_entries) == 1

    log_entries = list(
        contract.events.LogNoArguments.get_logs(from_block=1, to_block=2)
    )
    assert len(log_entries) == 0


def test_contract_get_logs_argument_filter(
    w3, emitter, wait_for_transaction, emitter_contract_event_ids
):
    contract = emitter

    txn_hashes = []
    event_id = emitter_contract_event_ids.LogTripleWithIndex
    # 1 = arg0
    # 4 = arg1
    # 1 = arg2
    txn_hashes.append(emitter.functions.logTriple(event_id, 1, 4, 1).transact())
    txn_hashes.append(emitter.functions.logTriple(event_id, 1, 1, 2).transact())
    txn_hashes.append(emitter.functions.logTriple(event_id, 1, 2, 2).transact())
    txn_hashes.append(emitter.functions.logTriple(event_id, 1, 3, 1).transact())
    for txn_hash in txn_hashes:
        wait_for_transaction(w3, txn_hash)

    all_logs = contract.events.LogTripleWithIndex.get_logs(from_block=1)
    assert len(all_logs) == 4

    # Filter all entries where arg1 in (1, 2)
    partial_logs = contract.events.LogTripleWithIndex.get_logs(
        from_block=1,
        argument_filters={"arg1": [1, 2]},
    )
    assert len(partial_logs) == 2

    # Filter all entries where arg0 == 1
    partial_logs = contract.events.LogTripleWithIndex.get_logs(
        from_block=1,
        argument_filters={"arg0": 1},
    )
    assert len(partial_logs) == 4


def test_get_logs_argument_filters_indexed_and_non_indexed_args(emitter):
    emitter.functions.logIndexedAndNotIndexedArgs(
        f"0xdead{'00' * 17}01",  # indexed address
        101,  # indexed uint256
        f"0xBEEf{'00' * 17}01",  # non-indexed address
        201,  # non-indexed uint256
        "This is the FIRST string arg.",  # non-indexed string
    ).transact()
    emitter.functions.logIndexedAndNotIndexedArgs(
        f"0xdEaD{'00' * 17}02",
        102,
        f"0xbeeF{'00' * 17}02",
        202,
        "This is the SECOND string arg.",
    ).transact()

    # get all logs
    logs_no_filter = emitter.events.LogIndexedAndNotIndexed.get_logs(from_block=1)
    assert len(logs_no_filter) == 2

    # filter for the second log by each of the indexed args and compare
    logs_filter_indexed_address = emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1,
        argument_filters={"indexedAddress": f"0xdEaD{'00' * 17}02"},
    )
    logs_filter_indexed_uint256 = emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1,
        argument_filters={"indexedUint256": 102},
    )
    assert len(logs_filter_indexed_address) == len(logs_filter_indexed_uint256) == 1
    assert (
        logs_filter_indexed_address[0]
        == logs_filter_indexed_uint256[0]
        == logs_no_filter[1]
    )

    # filter for the first log by non-indexed address
    logs_filter_non_indexed_address = emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1,
        argument_filters={"nonIndexedAddress": f"0xBEEf{'00' * 17}01"},
    )
    assert len(logs_filter_non_indexed_address) == 1
    assert logs_filter_non_indexed_address[0] == logs_no_filter[0]

    # filter for the second log by non-indexed uint256 and string separately
    logs_filter_non_indexed_uint256 = emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1,
        argument_filters={"nonIndexedUint256": 202},
    )
    logs_filter_non_indexed_string = emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1,
        argument_filters={"nonIndexedString": "SECOND"},
    )
    assert len(logs_filter_non_indexed_uint256) == 1
    assert len(logs_filter_non_indexed_string) == 1
    assert (
        logs_filter_non_indexed_uint256[0]
        == logs_filter_non_indexed_string[0]
        == logs_no_filter[1]
    )

    # filter by both string and uint256, non-indexed
    logs_filter_non_indexed_uint256_and_string = (
        emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={
                "nonIndexedUint256": 201,
                "nonIndexedString": "FIRST",
            },
        )
    )
    assert len(logs_filter_non_indexed_uint256_and_string) == 1
    assert logs_filter_non_indexed_uint256_and_string[0] == logs_no_filter[0]

    # every filter must match: indexed and non-indexed args from different logs
    logs_filter_indexed_and_non_indexed_mismatch = (
        emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"indexedUint256": 102, "nonIndexedUint256": 201},
        )
    )
    assert logs_filter_indexed_and_non_indexed_mismatch == []

    # every filter must match: non-indexed args from different logs
    logs_filter_non_indexed_mismatch = emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1,
        argument_filters={"nonIndexedUint256": 201, "nonIndexedString": "SECOND"},
    )
    assert logs_filter_non_indexed_mismatch == []


def test_get_logs_argument_filters_key_validation(
    emitter,
):
    with pytest.raises(
        Web3ValidationError,
        match="all argument names must be present in the contract's event ABI",
    ):
        emitter.events.LogIndexedAndNotIndexed.get_logs(
            argument_filters={"nonExistentKey": "Value shouldn't matter"},
        )


# --- async --- #


def test_async_contract_get_available_events(
    async_emitter,
):
    """We can iterate over available contract events"""
    contract = async_emitter
    events = list(contract.events)
    assert len(events) == len(EMITTER_ENUM)


@pytest.mark.asyncio
async def test_async_contract_get_logs_all(
    async_w3,
    async_emitter,
    async_wait_for_transaction,
    emitter_contract_event_ids,
):
    contract = async_emitter
    event_id = emitter_contract_event_ids.LogNoArguments

    txn_hash = await contract.functions.logNoArgs(event_id).transact()
    await async_wait_for_transaction(async_w3, txn_hash)

    contract_logs = await contract.events.LogNoArguments.get_logs()
    log_entries = list(contract_logs)
    assert len(log_entries) == 1
    assert log_entries[0]["transactionHash"] == txn_hash


@pytest.mark.asyncio
async def test_async_contract_get_logs_range(
    async_w3,
    async_emitter,
    async_wait_for_transaction,
    emitter_contract_event_ids,
):
    contract = async_emitter
    event_id = emitter_contract_event_ids.LogNoArguments

    eth_block_number = await async_w3.eth.block_number
    assert eth_block_number == 2
    txn_hash = await contract.functions.logNoArgs(event_id).transact()
    # Mined as block 3
    await async_wait_for_transaction(async_w3, txn_hash)
    eth_block_number = await async_w3.eth.block_number
    assert eth_block_number == 3

    contract_logs = await contract.events.LogNoArguments.get_logs()
    log_entries = list(contract_logs)
    assert len(log_entries) == 1

    contract_logs = await contract.events.LogNoArguments.get_logs(
        from_block=2, to_block=3
    )
    log_entries = list(contract_logs)
    assert len(log_entries) == 1

    contract_logs = await contract.events.LogNoArguments.get_logs(
        from_block=1, to_block=2
    )
    log_entries = list(contract_logs)
    assert len(log_entries) == 0


@pytest.mark.asyncio
async def test_async_contract_get_logs_argument_filter(
    async_w3, async_emitter, async_wait_for_transaction, emitter_contract_event_ids
):
    contract = async_emitter

    txn_hashes = []
    event_id = emitter_contract_event_ids.LogTripleWithIndex
    # 1 = arg0
    # 4 = arg1
    # 1 = arg2
    txn_hashes.append(
        await async_emitter.functions.logTriple(event_id, 1, 4, 1).transact()
    )
    txn_hashes.append(
        await async_emitter.functions.logTriple(event_id, 1, 1, 2).transact()
    )
    txn_hashes.append(
        await async_emitter.functions.logTriple(event_id, 1, 2, 2).transact()
    )
    txn_hashes.append(
        await async_emitter.functions.logTriple(event_id, 1, 3, 1).transact()
    )
    for txn_hash in txn_hashes:
        await async_wait_for_transaction(async_w3, txn_hash)

    all_logs = await contract.events.LogTripleWithIndex.get_logs(from_block=1)
    assert len(all_logs) == 4

    # Filter all entries where arg1 in (1, 2)
    partial_logs = await contract.events.LogTripleWithIndex.get_logs(
        from_block=1,
        argument_filters={"arg1": [1, 2]},
    )
    assert len(partial_logs) == 2

    # Filter all entries where arg0 == 1
    partial_logs = await contract.events.LogTripleWithIndex.get_logs(
        from_block=1,
        argument_filters={"arg0": 1},
    )
    assert len(partial_logs) == 4


@pytest.mark.asyncio
async def test_async_get_logs_argument_filters_indexed_and_non_indexed_args(
    async_emitter,
):
    await async_emitter.functions.logIndexedAndNotIndexedArgs(
        f"0xdead{'00' * 17}01",  # indexed address
        101,  # indexed uint256
        f"0xBEEf{'00' * 17}01",  # non-indexed address
        201,  # non-indexed uint256
        "This is the FIRST string arg.",  # non-indexed string
    ).transact()
    await async_emitter.functions.logIndexedAndNotIndexedArgs(
        f"0xdEaD{'00' * 17}02",
        102,
        f"0xbeeF{'00' * 17}02",
        202,
        "This is the SECOND string arg.",
    ).transact()

    # get all logs
    logs_no_filter = await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
        from_block=1
    )
    assert len(logs_no_filter) == 2

    # filter for the second log by each of the indexed args and compare
    logs_filter_indexed_address = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"indexedAddress": f"0xdEaD{'00' * 17}02"},
        )
    )
    logs_filter_indexed_uint256 = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"indexedUint256": 102},
        )
    )
    assert len(logs_filter_indexed_address) == len(logs_filter_indexed_uint256) == 1
    assert (
        logs_filter_indexed_address[0]
        == logs_filter_indexed_uint256[0]
        == logs_no_filter[1]
    )

    # filter for the first log by non-indexed address
    logs_filter_non_indexed_address = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"nonIndexedAddress": f"0xBEEf{'00' * 17}01"},
        )
    )
    assert len(logs_filter_non_indexed_address) == 1
    assert logs_filter_non_indexed_address[0] == logs_no_filter[0]

    # filter for the second log by non-indexed uint256 and string separately
    logs_filter_non_indexed_uint256 = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"nonIndexedUint256": 202},
        )
    )
    logs_filter_non_indexed_string = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"nonIndexedString": "SECOND"},
        )
    )
    assert len(logs_filter_non_indexed_uint256) == 1
    assert len(logs_filter_non_indexed_string) == 1
    assert (
        logs_filter_non_indexed_uint256[0]
        == logs_filter_non_indexed_string[0]
        == logs_no_filter[1]
    )

    # filter by both string and uint256, non-indexed
    logs_filter_non_indexed_uint256_and_string = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={
                "nonIndexedUint256": 201,
                "nonIndexedString": "FIRST",
            },
        )
    )
    assert len(logs_filter_non_indexed_uint256_and_string) == 1
    assert logs_filter_non_indexed_uint256_and_string[0] == logs_no_filter[0]

    # every filter must match: indexed and non-indexed args from different logs
    logs_filter_indexed_and_non_indexed_mismatch = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"indexedUint256": 102, "nonIndexedUint256": 201},
        )
    )
    assert logs_filter_indexed_and_non_indexed_mismatch == []

    # every filter must match: non-indexed args from different logs
    logs_filter_non_indexed_mismatch = (
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            from_block=1,
            argument_filters={"nonIndexedUint256": 201, "nonIndexedString": "SECOND"},
        )
    )
    assert logs_filter_non_indexed_mismatch == []


@pytest.mark.asyncio
async def test_async_get_logs_argument_filters_key_validation(
    async_emitter,
):
    with pytest.raises(
        Web3ValidationError,
        match="all argument names must be present in the contract's event ABI",
    ):
        await async_emitter.events.LogIndexedAndNotIndexed.get_logs(
            argument_filters={"nonExistentKey": "Value shouldn't matter"},
        )
