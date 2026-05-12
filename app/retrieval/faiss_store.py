import json
from pathlib import Path
from typing import Any

import numpy as np

from app.config.settings import settings
from app.models import Chunk, ScoredChunk
from app.retrieval.filter import match_filters
from app.retrieval.vector_store import VectorStore


class FaissVectorStore(VectorStore):
    def __init__(self, index_path: Path | None = None) -> None:
        self.index_path = index_path or settings.faiss_index_path
        self.chunks_path = self.index_path.with_suffix(".chunks.json")
        self._chunks: list[Chunk] | None = None
        self._faiss = self._load_faiss()

    async def upsert(self, chunks: list[Chunk]) -> None:
        existing = await self._load_chunks()
        ids = {chunk.id for chunk in chunks}
        merged = [chunk for chunk in existing if chunk.id not in ids] + chunks
        self._chunks = merged
        self._save_chunks(merged)
        self._save_faiss_index(merged)

    async def search(
        self, query_vec: list[float], top_k: int, filters: dict[str, Any] | None = None
    ) -> list[ScoredChunk]:
        chunks = [chunk for chunk in await self._load_chunks() if match_filters(chunk.metadata, filters)]
        if not chunks:
            return []
        query = self._normalize(np.asarray(query_vec, dtype=np.float32))
        matrix = np.asarray(
            [self._normalize(np.asarray(chunk.embedding, dtype=np.float32)) for chunk in chunks],
            dtype=np.float32,
        )
        scores = matrix @ query
        order = np.argsort(scores)[::-1][:top_k]
        return [
            ScoredChunk(**chunks[index].model_dump(), score=float(scores[index]))
            for index in order
        ]

    async def delete(self, doc_id: str) -> int:
        chunks = await self._load_chunks()
        kept = [chunk for chunk in chunks if chunk.metadata.get("doc_id") != doc_id]
        deleted = len(chunks) - len(kept)
        self._chunks = kept
        self._save_chunks(kept)
        self._save_faiss_index(kept)
        return deleted

    async def list_documents(self) -> list[dict[str, Any]]:
        docs: dict[str, dict[str, Any]] = {}
        for chunk in await self._load_chunks():
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

    async def _load_chunks(self) -> list[Chunk]:
        if self._chunks is not None:
            return self._chunks
        if not self.chunks_path.exists():
            self._chunks = []
            return self._chunks
        data = json.loads(self.chunks_path.read_text(encoding="utf-8"))
        self._chunks = [Chunk(**item) for item in data.get("chunks", [])]
        return self._chunks

    def _save_chunks(self, chunks: list[Chunk]) -> None:
        self.chunks_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"chunks": [chunk.model_dump() for chunk in chunks]}
        self.chunks_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _save_faiss_index(self, chunks: list[Chunk]) -> None:
        if self._faiss is None:
            return
        vectors = [chunk.embedding for chunk in chunks if chunk.embedding]
        if not vectors:
            if self.index_path.exists():
                self.index_path.unlink()
            return
        matrix = np.asarray(vectors, dtype=np.float32)
        matrix = np.asarray([self._normalize(vector) for vector in matrix], dtype=np.float32)
        index = self._faiss.IndexFlatIP(matrix.shape[1])
        index.add(matrix)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self._faiss.write_index(index, str(self.index_path))

    def _load_faiss(self):
        try:
            import faiss
        except ImportError:
            return None
        return faiss

    def _normalize(self, vector: np.ndarray) -> np.ndarray:
        norm = float(np.linalg.norm(vector))
        return vector / norm if norm else vector
