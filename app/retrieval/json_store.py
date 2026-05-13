import json
from pathlib import Path
from typing import Any

import numpy as np

from app.config.settings import settings
from app.models import Chunk, ScoredChunk
from app.retrieval.filter import match_filters
from app.retrieval.hybrid import bm25_scores, reciprocal_rank_fusion
from app.retrieval.vector_store import VectorStore


class JsonVectorStore(VectorStore):
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.index_path
        self._chunks: list[Chunk] | None = None

    async def upsert(self, chunks: list[Chunk]) -> None:
        existing = await self._load()
        ids = {chunk.id for chunk in chunks}
        merged = [chunk for chunk in existing if chunk.id not in ids] + chunks
        self._chunks = merged
        self._save(merged)

    async def search(
        self,
        query_vec: list[float],
        top_k: int,
        filters: dict[str, Any] | None = None,
        query_text: str | None = None,
    ) -> list[ScoredChunk]:
        chunks = [chunk for chunk in await self._load() if match_filters(chunk.metadata, filters)]
        query = np.asarray(query_vec, dtype=np.float32)
        results: list[ScoredChunk] = []
        vector_scores: list[float] = []
        for chunk in chunks:
            if not chunk.embedding:
                continue
            vector = np.asarray(chunk.embedding, dtype=np.float32)
            denom = float(np.linalg.norm(query) * np.linalg.norm(vector))
            score = float(np.dot(query, vector) / denom) if denom else 0.0
            results.append(ScoredChunk(**chunk.model_dump(), score=score))
            vector_scores.append(score)
        if query_text and results:
            lexical_scores = bm25_scores(query_text, [item.text for item in results])
            fused_scores = reciprocal_rank_fusion(vector_scores, lexical_scores)
            for item, fused_score in zip(results, fused_scores):
                item.score = fused_score
        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    async def delete(self, doc_id: str) -> int:
        chunks = await self._load()
        kept = [chunk for chunk in chunks if chunk.metadata.get("doc_id") != doc_id]
        deleted = len(chunks) - len(kept)
        self._chunks = kept
        self._save(kept)
        return deleted

    async def list_documents(self) -> list[dict[str, Any]]:
        docs: dict[str, dict[str, Any]] = {}
        for chunk in await self._load():
            doc_id = str(chunk.metadata.get("doc_id", "unknown"))
            doc = docs.setdefault(
                doc_id,
                {
                    "doc_id": doc_id,
                    "doc_title": chunk.metadata.get("doc_title", ""),
                    "doc_type": chunk.metadata.get("doc_type", ""),
                    "chunk_count": 0,
                    "metadata": {},
                },
            )
            doc["chunk_count"] += 1
            doc["metadata"].update(chunk.metadata)
        return list(docs.values())

    async def _load(self) -> list[Chunk]:
        if self._chunks is not None:
            return self._chunks
        if not self.path.exists():
            self._chunks = []
            return self._chunks
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._chunks = [Chunk(**item) for item in data.get("chunks", [])]
        return self._chunks

    def _save(self, chunks: list[Chunk]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"chunks": [chunk.model_dump() for chunk in chunks]}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
