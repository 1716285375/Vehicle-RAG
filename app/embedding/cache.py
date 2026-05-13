import hashlib
import json
from collections.abc import Sequence

from app.config.settings import settings
from app.infra.redis_client import CacheBackend, cache


def text_cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class CachedEmbedder:
    def __init__(
        self,
        inner,
        cache_backend: CacheBackend | None = None,
        ttl: int | None = None,
        prefix: str = "embedding",
    ) -> None:
        self.inner = inner
        self.cache = cache_backend or cache
        self.ttl = ttl or settings.embedding_cache_ttl
        self.prefix = prefix

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: Sequence[str], batch_size: int = 32) -> list[list[float]]:
        results: list[list[float] | None] = [None] * len(texts)
        missing_indexes: list[int] = []
        missing_texts: list[str] = []

        for index, text in enumerate(texts):
            cached = await self.cache.get(self._key(text))
            if cached is None:
                missing_indexes.append(index)
                missing_texts.append(text)
                continue
            results[index] = json.loads(cached)

        if missing_texts:
            embedded = await self.inner.embed_batch(missing_texts, batch_size=batch_size)
            for index, text, vector in zip(missing_indexes, missing_texts, embedded):
                results[index] = vector
                await self.cache.setex(self._key(text), self.ttl, json.dumps(vector))

        return [vector for vector in results if vector is not None]

    def _key(self, text: str) -> str:
        return f"{self.prefix}:{text_cache_key(text)}"
