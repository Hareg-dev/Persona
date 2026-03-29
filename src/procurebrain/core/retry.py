import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar


T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    retries: int = 3,
    base_delay: float = 0.5,
) -> T:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return await operation()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == retries - 1:
                raise
            await asyncio.sleep(base_delay * (2**attempt))
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_async failed without capturing an exception")


def retry_sync(
    operation: Callable[[], T],
    retries: int = 3,
    base_delay: float = 0.5,
) -> T:
    import time

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == retries - 1:
                raise
            time.sleep(base_delay * (2**attempt))
    if last_error is not None:
        raise last_error
    raise RuntimeError("retry_sync failed without capturing an exception")
