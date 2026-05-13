import asyncio

from app.embedding import CachedEmbedder
from app.infra.redis_client import InMemoryTTLCache


class CountingEmbedder:
    def __init__(self) -> None:
        self.calls = 0

    async def embed_batch(self, texts, batch_size=32):
        self.calls += 1
        return [[float(len(text))] for text in texts]


def test_cached_embedder_reuses_cached_vectors():
    asyncio.run(_run_cached_embedder_reuses_cached_vectors())


async def _run_cached_embedder_reuses_cached_vectors():
    inner = CountingEmbedder()
    embedder = CachedEmbedder(inner, cache_backend=InMemoryTTLCache(), ttl=60)

    assert await embedder.embed("AUTOHOLD") == [8.0]
    assert await embedder.embed("AUTOHOLD") == [8.0]
    assert inner.calls == 1
