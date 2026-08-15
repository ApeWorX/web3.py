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
async def test_async_lock_cancellation_safety() -> None:
    pool = ThreadPoolExecutor(max_workers=5)
    lock = threading.Lock()

    async def worker(duration: float, timeout: float) -> None:
        try:
            async def _run() -> None:
                async with async_lock(pool, lock):
                    await asyncio.sleep(duration)

            await asyncio.wait_for(_run(), timeout=timeout)
        except asyncio.TimeoutError:
            pass

    tasks = [
        asyncio.create_task(worker(duration=0.03, timeout=0.01))
        for _ in range(25)
    ]
    await asyncio.gather(*tasks)
    await asyncio.sleep(0.1)

    assert not lock.locked()

    async with async_lock(pool, lock):
        assert lock.locked()
    assert not lock.locked()

    pool.shutdown(wait=True)
