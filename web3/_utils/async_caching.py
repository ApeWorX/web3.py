import asyncio
from collections.abc import AsyncGenerator
from concurrent.futures import (
    ThreadPoolExecutor,
)
import contextlib
import threading
from typing import Any


@contextlib.asynccontextmanager
async def async_lock(
    thread_pool: ThreadPoolExecutor, lock: threading.Lock
) -> AsyncGenerator[None, None]:
    loop = asyncio.get_event_loop()
    acquire_task = loop.run_in_executor(thread_pool, lock.acquire)
    acquired = False

    try:
        await asyncio.shield(acquire_task)
        acquired = True
        yield
    finally:
        if acquired:
            lock.release()
        else:

            def _release_on_acquire(fut: asyncio.Future[Any]) -> None:
                try:
                    if fut.result():
                        lock.release()
                except Exception:
                    pass

            acquire_task.add_done_callback(_release_on_acquire)
