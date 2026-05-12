from abc import ABC, abstractmethod
from typing import Any

from app.models import Chunk, ScoredChunk


class VectorStore(ABC):
    @abstractmethod
    async def upsert(self, chunks: list[Chunk]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search(
        self, query_vec: list[float], top_k: int, filters: dict[str, Any] | None = None
    ) -> list[ScoredChunk]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, doc_id: str) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list_documents(self) -> list[dict[str, Any]]:
        raise NotImplementedError

