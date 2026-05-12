import time
from typing import Protocol

from app.config.settings import settings


class CacheBackend(Protocol):
    async def get(self, key: str) -> str | None:
        raise NotImplementedError

    async def setex(self, key: str, ttl: int, value: str) -> None:
        raise NotImplementedError


class InMemoryTTLCache:
    def __init__(self) -> None:
        self._values: dict[str, tuple[float, str]] = {}

    async def get(self, key: str) -> str | None:
        item = self._values.get(key)
        if item is None:
            return None
        expires_at, value = item
        if expires_at <= time.monotonic():
            self._values.pop(key, None)
            return None
        return value

    async def setex(self, key: str, ttl: int, value: str) -> None:
        if ttl <= 0:
            self._values.pop(key, None)
            return
        self._values[key] = (time.monotonic() + ttl, value)

    def clear(self) -> None:
        self._values.clear()


class RedisCache:
    def __init__(self, redis_url: str) -> None:
        try:
            from redis.asyncio import Redis
        except ImportError as exc:
            raise RuntimeError("Install the redis extra to use RedisCache.") from exc
        self._client = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        await self._client.setex(key, ttl, value)


def build_cache(redis_url: str | None = None) -> CacheBackend:
    if redis_url:
        try:
            return RedisCache(redis_url)
        except RuntimeError:
            return InMemoryTTLCache()
    return InMemoryTTLCache()


cache = build_cache(settings.redis_url)
