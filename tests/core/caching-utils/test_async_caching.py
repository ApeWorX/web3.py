import pytest
import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
import threading

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
async def test_async_lock_cancellation_while_blocked_does_not_release_existing_owner() -> (
    None
):
    pool = ThreadPoolExecutor(max_workers=4)
    lock = threading.Lock()

    # 1. Task A acquires and holds the lock directly
    assert lock.acquire(blocking=False)
    assert lock.locked()

    started = asyncio.Event()

    async def waiter() -> None:
        started.set()
        async with async_lock(pool, lock):
            pass

    # 2. Task B enters async_lock and blocks waiting for the lock in executor
    task_b = asyncio.create_task(waiter())
    await started.wait()
    await asyncio.sleep(0.02)

    # 3. Cancel Task B while Task A still owns the lock
    task_b.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task_b

    # INVARIANT: Task B must NOT have released Task A's lock in its finally block!
    assert lock.locked(), "Task A's lock must remain held after Task B was cancelled"

    # 4. Task A releases its lock cleanly
    lock.release()
    await asyncio.sleep(0.05)

    # INVARIANT: Orphan executor acquisition must not permanently poison the lock
    assert not lock.locked(), "Lock must be released and not permanently retained"

    # 5. Subsequent waiter (Task C) acquires successfully
    acquired_c = False
    async with async_lock(pool, lock):
        acquired_c = True
        assert lock.locked()
    assert acquired_c
    assert not lock.locked()

    pool.shutdown(wait=True)


@pytest.mark.asyncio
async def test_async_lock_cancellation_after_acquisition_releases_lock() -> None:
    pool = ThreadPoolExecutor(max_workers=2)
    lock = threading.Lock()

    entered = asyncio.Event()

    async def cancel_inside_body() -> None:
        async with async_lock(pool, lock):
            assert lock.locked()
            entered.set()
            # Wait until cancelled
            await asyncio.sleep(10)

    task = asyncio.create_task(cancel_inside_body())
    await entered.wait()

    # Cancel while holding the lock inside the body
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    # INVARIANT: Lock must be released after cancellation inside body
    assert not lock.locked(), (
        "Lock must be released when task is cancelled inside context body"
    )

    # Subsequent task can acquire
    async with async_lock(pool, lock):
        assert lock.locked()
    assert not lock.locked()

    pool.shutdown(wait=True)


@pytest.mark.asyncio
async def test_async_lock_multiple_cancelled_waiters_drain_safely() -> None:
    pool = ThreadPoolExecutor(max_workers=6)
    lock = threading.Lock()

    assert lock.acquire(blocking=False)
    assert lock.locked()

    started_count = 0
    all_started = asyncio.Event()

    async def waiter() -> None:
        nonlocal started_count
        started_count += 1
        if started_count == 5:
            all_started.set()
        async with async_lock(pool, lock):
            pass

    tasks = [asyncio.create_task(waiter()) for _ in range(5)]
    await all_started.wait()
    await asyncio.sleep(0.02)

    # Cancel all 5 waiters
    for t in tasks:
        t.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    # Initial holder releases lock
    lock.release()
    await asyncio.sleep(0.08)

    # Verify all 5 orphaned acquisitions drained and released safely
    assert not lock.locked(), "Lock must not remain locked after queued waiters drain"

    # Subsequent task acquires without deadlock
    async with async_lock(pool, lock):
        assert lock.locked()
    assert not lock.locked()

    pool.shutdown(wait=True)


@pytest.mark.asyncio
async def test_async_lock_already_done_future_cancellation_releases_lock() -> None:
    pool = ThreadPoolExecutor(max_workers=2)
    lock = threading.Lock()

    # Verify that if cancel() is invoked on a task where the lock was acquired
    # but context has not yielded or is interrupted, the lock releases cleanly.
    acquired_flag = False

    async def acquire_and_cancel_self() -> None:
        nonlocal acquired_flag
        async with async_lock(pool, lock):
            acquired_flag = True
            current_task = asyncio.current_task()
            assert current_task is not None
            current_task.cancel()
            await asyncio.sleep(0)

    task = asyncio.create_task(acquire_and_cancel_self())
    with pytest.raises(asyncio.CancelledError):
        await task

    assert acquired_flag
    assert not lock.locked()

    pool.shutdown(wait=True)
