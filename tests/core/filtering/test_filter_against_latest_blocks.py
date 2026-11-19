import pytest

from hexbytes import (
    HexBytes,
)

from web3._utils.threads import (
    Timeout,
)


def test_sync_filter_against_latest_blocks(w3, sleep_interval, wait_for_block):
    txn_filter = w3.eth.filter("latest")
    current_block = w3.eth.block_number
    wait_for_block(w3, current_block + 3)

    found_block_hashes = []
    with Timeout(5) as timeout:
        while len(found_block_hashes) < 3:
            found_block_hashes.extend(txn_filter.get_new_entries())
            timeout.sleep(sleep_interval())

    assert len(found_block_hashes) == 3

    expected_block_hashes = [
        w3.eth.get_block(n + 1).hash for n in range(current_block, current_block + 3)
    ]
    assert found_block_hashes == expected_block_hashes


def test_block_filter_only_returns_new_blocks(w3):
    block_filter = w3.eth.filter("latest")

    for count in (0, 2, 0, 3, 0, 1, 0):
        hashes = w3.provider.ethereum_tester.mine_blocks(count) if count else []
        assert block_filter.get_new_entries() == [HexBytes(h) for h in hashes]


def test_block_filters_track_changes_independently(w3):
    first = w3.eth.filter("latest")
    initial = w3.provider.ethereum_tester.mine_blocks(2)
    second = w3.eth.filter("latest")

    assert first.get_new_entries() == [HexBytes(h) for h in initial]
    assert second.get_new_entries() == []

    hashes = w3.provider.ethereum_tester.mine_blocks(2)
    expected = [HexBytes(h) for h in hashes]
    assert second.get_new_entries() == expected
    assert first.get_new_entries() == expected
    assert first.get_new_entries() == []
    assert second.get_new_entries() == []


# --- async --- #


@pytest.mark.asyncio
async def test_async_filter_against_latest_blocks(
    async_w3, sleep_interval, async_wait_for_block
):
    txn_filter = await async_w3.eth.filter("latest")
    current_block = await async_w3.eth.block_number
    await async_wait_for_block(async_w3, current_block + 3)

    found_block_hashes = []
    with Timeout(5) as timeout:
        while len(found_block_hashes) < 3:
            new_entries = await txn_filter.get_new_entries()
            found_block_hashes.extend(new_entries)
            await timeout.async_sleep(sleep_interval())

    assert len(found_block_hashes) == 3

    expected_block_hashes = []
    for n in range(current_block, current_block + 3):
        block = await async_w3.eth.get_block(n + 1)
        expected_block_hashes.append(block.hash)

    assert found_block_hashes == expected_block_hashes


@pytest.mark.asyncio
async def test_async_block_filter_only_returns_new_blocks(async_w3):
    block_filter = await async_w3.eth.filter("latest")

    for count in (0, 2, 0, 3, 0, 1, 0):
        hashes = async_w3.provider.ethereum_tester.mine_blocks(count) if count else []
        assert await block_filter.get_new_entries() == [HexBytes(h) for h in hashes]


@pytest.mark.asyncio
async def test_async_block_filters_track_changes_independently(async_w3):
    first = await async_w3.eth.filter("latest")
    initial = async_w3.provider.ethereum_tester.mine_blocks(2)
    second = await async_w3.eth.filter("latest")

    assert await first.get_new_entries() == [HexBytes(h) for h in initial]
    assert await second.get_new_entries() == []

    hashes = async_w3.provider.ethereum_tester.mine_blocks(2)
    expected = [HexBytes(h) for h in hashes]
    assert await second.get_new_entries() == expected
    assert await first.get_new_entries() == expected
    assert await first.get_new_entries() == []
    assert await second.get_new_entries() == []
