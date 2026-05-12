import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def retry_async(fn: Callable[[], Awaitable[T]], attempts: int = 3, delay: float = 0.2) -> T:
    last_error: Exception | None = None
    for index in range(attempts):
        try:
            return await fn()
        except Exception as exc:
            last_error = exc
            if index < attempts - 1:
                await asyncio.sleep(delay * (index + 1))
    assert last_error is not None
    raise last_error

