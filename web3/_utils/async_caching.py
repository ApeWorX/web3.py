import asyncio
from collections.abc import AsyncGenerator
from concurrent.futures import (
    ThreadPoolExecutor,
)
import contextlib
import threading


@contextlib.asynccontextmanager
async def async_lock(
    thread_pool: ThreadPoolExecutor, lock: threading.Lock
) -> AsyncGenerator[None, None]:
    loop = asyncio.get_running_loop()
    acquired = False
    # Shield the acquire: if this task is cancelled (e.g. an
    # `asyncio.wait_for` timeout) while the executor thread is blocked in
    # `lock.acquire()`, the executor thread keeps running and would otherwise
    # hold the lock forever with no one left to release it. If it acquires
    # the lock after we are gone, the done-callback below releases it.
    # See https://github.com/ethereum/web3.py/issues/3867
    acquire_future = loop.run_in_executor(thread_pool, lock.acquire)
    try:
        await asyncio.shield(acquire_future)
        acquired = True
    except asyncio.CancelledError:

        def _release_if_held(future: asyncio.Future[bool]) -> None:
            if not future.cancelled() and lock.locked():
                lock.release()

        acquire_future.add_done_callback(_release_if_held)
        raise
    try:
        yield
    finally:
        if acquired:
            lock.release()
