import asyncio
from concurrent.futures import (
    ThreadPoolExecutor,
)
import contextlib
import threading
from typing import (
    AsyncGenerator,
)


@contextlib.asynccontextmanager
async def async_lock(
    thread_pool: ThreadPoolExecutor, lock: threading.Lock
) -> AsyncGenerator[None, None]:
    loop = asyncio.get_event_loop()
    fut = loop.run_in_executor(thread_pool, lock.acquire)
    acquired = False
    try:
        await asyncio.shield(fut)
        acquired = True
        yield
    except asyncio.CancelledError:
        if not acquired:
            fut.add_done_callback(lambda _: lock.release())
        raise
    finally:
        if acquired:
            lock.release()
