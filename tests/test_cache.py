import asyncio

from app.infra.redis_client import InMemoryTTLCache


def test_in_memory_cache_returns_value_before_ttl():
    asyncio.run(_run_cache_returns_value_before_ttl())


async def _run_cache_returns_value_before_ttl():
    cache = InMemoryTTLCache()
    await cache.setex("key", 60, "value")
    assert await cache.get("key") == "value"


def test_in_memory_cache_drops_zero_ttl():
    asyncio.run(_run_cache_drops_zero_ttl())


async def _run_cache_drops_zero_ttl():
    cache = InMemoryTTLCache()
    await cache.setex("key", 0, "value")
    assert await cache.get("key") is None
