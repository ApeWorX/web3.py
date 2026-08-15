import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
import contextlib
import threading
from typing import (
    Any,
    AsyncGenerator,
)


@contextlib.asynccontextmanager
async def async_lock(
    thread_pool: ThreadPoolExecutor, lock: threading.Lock
) -> AsyncGenerator[None, None]:
    loop = asyncio.get_event_loop()
    fut: asyncio.Future[Any] = loop.run_in_executor(thread_pool, lock.acquire)
    acquired = False

    def _release_if_acquired(future: asyncio.Future[Any]) -> None:
        try:
            if not future.cancelled() and future.exception() is None and future.result():
                lock.release()
        except (RuntimeError, Exception):
            pass

    try:
        await asyncio.shield(fut)
        acquired = True
        yield
    except asyncio.CancelledError:
        if not acquired:
            fut.add_done_callback(_release_if_acquired)
        raise
    finally:
        if acquired:
            lock.release()
