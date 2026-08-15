import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
import threading
import pytest

from web3._utils.async_caching import (
    async_lock,
)


@pytest.mark.asyncio
async def test_async_lock_normal_acquisition() -> None:
    pool = ThreadPoolExecutor(max_workers=2)
    lock = threading.Lock()

    assert not lock.locked()
    async with async_lock(pool, lock):
        assert lock.locked()
    assert not lock.locked()

    pool.shutdown(wait=True)


@pytest.mark.asyncio
async def test_async_lock_deterministic_cancellation_while_blocked() -> None:
    pool = ThreadPoolExecutor(max_workers=4)
    lock = threading.Lock()

    # 1. Thread holds lock initially
    lock.acquire()
    assert lock.locked()

    started = asyncio.Event()

    async def waiter() -> None:
        started.set()
        async with async_lock(pool, lock):
            pass

    task = asyncio.create_task(waiter())
    await started.wait()
    await asyncio.sleep(0.02)

    # 2. Cancel waiter while lock is held
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    # 3. Initial holder releases lock
    lock.release()
    await asyncio.sleep(0.05)

    # 4. Verify lock was drained and unlocked by cleanup callback
    assert not lock.locked()

    # 5. Subsequent tasks can acquire lock cleanly
    async with async_lock(pool, lock):
        assert lock.locked()
    assert not lock.locked()

    pool.shutdown(wait=True)


@pytest.mark.asyncio
async def test_async_lock_multiple_cancelled_waiters_drain_safely() -> None:
    pool = ThreadPoolExecutor(max_workers=6)
    lock = threading.Lock()

    lock.acquire()
    started_count = 0
    started_event = asyncio.Event()

    async def waiter() -> None:
        nonlocal started_count
        started_count += 1
        if started_count == 5:
            started_event.set()
        async with async_lock(pool, lock):
            pass

    tasks = [asyncio.create_task(waiter()) for _ in range(5)]
    await started_event.wait()
    await asyncio.sleep(0.02)

    # Cancel all 5 waiters
    for t in tasks:
        t.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    # Release initial holder
    lock.release()
    await asyncio.sleep(0.08)

    # Verify all 5 orphaned acquisitions drained and released safely
    assert not lock.locked()

    async with async_lock(pool, lock):
        assert lock.locked()
    assert not lock.locked()

    pool.shutdown(wait=True)
