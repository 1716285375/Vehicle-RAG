import asyncio
import hashlib
import math
from collections.abc import Sequence

import numpy as np

from app.config.settings import settings


class HashEmbedder:
    """Deterministic local embedding for development and tests."""

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.embedding_dim

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: Sequence[str], batch_size: int = 32) -> list[list[float]]:
        return [self._embed_sync(text) for text in texts]

    def _embed_sync(self, text: str) -> list[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = self._tokens(text)
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "little")
            idx = value % self.dim
            sign = 1.0 if (value >> 8) & 1 else -1.0
            vec[idx] += sign
        norm = float(np.linalg.norm(vec))
        if norm > 0:
            vec /= norm
        return vec.tolist()

    def _tokens(self, text: str) -> list[str]:
        normalized = text.lower()
        words: list[str] = []
        buf: list[str] = []
        for char in normalized:
            if char.isascii() and char.isalnum():
                buf.append(char)
            else:
                if buf:
                    words.append("".join(buf))
                    buf = []
                if not char.isspace():
                    words.append(char)
        if buf:
            words.append("".join(buf))
        return words or [normalized]


class BGEM3Embedder:
    def __init__(self, model_path: str = "BAAI/bge-m3", device: str = "cpu") -> None:
        from FlagEmbedding import BGEM3FlagModel

        self.model = BGEM3FlagModel(model_path, use_fp16=device != "cpu", device=device)

    async def embed(self, text: str) -> list[float]:
        return (await self.embed_batch([text]))[0]

    async def embed_batch(self, texts: Sequence[str], batch_size: int = 32) -> list[list[float]]:
        result = await asyncio.to_thread(
            self.model.encode,
            list(texts),
            batch_size=batch_size,
            return_dense=True,
        )
        vectors = result["dense_vecs"]
        return [self._normalize(vector).tolist() for vector in vectors]

    def _normalize(self, vector: Sequence[float]) -> np.ndarray:
        arr = np.asarray(vector, dtype=np.float32)
        norm = math.sqrt(float(np.dot(arr, arr)))
        return arr / norm if norm else arr

