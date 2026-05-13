import json
from typing import Any

import numpy as np

from app.config.settings import settings
from app.models import Chunk, ScoredChunk
from app.retrieval.filter import match_filters
from app.retrieval.vector_store import VectorStore


class MilvusVectorStore(VectorStore):
    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        collection_name: str | None = None,
        dim: int | None = None,
    ) -> None:
        self.host = host or settings.milvus_host
        self.port = port or settings.milvus_port
        self.collection_name = collection_name or settings.milvus_collection
        self.dim = dim or settings.embedding_dim
        self._pymilvus = self._load_pymilvus()
        self._collection = None

    async def upsert(self, chunks: list[Chunk]) -> None:
        collection = self._get_collection()
        rows = [
            [
                chunk.id,
                str(chunk.metadata.get("doc_id", "")),
                chunk.text,
                json.dumps(chunk.metadata, ensure_ascii=False),
                chunk.embedding or [0.0] * self.dim,
            ]
            for chunk in chunks
        ]
        if rows:
            collection.insert(list(map(list, zip(*rows))))
            collection.flush()

    async def search(
        self,
        query_vec: list[float],
        top_k: int,
        filters: dict[str, Any] | None = None,
        query_text: str | None = None,
    ) -> list[ScoredChunk]:
        collection = self._get_collection()
        collection.load()
        results = collection.search(
            data=[np.asarray(query_vec, dtype=np.float32).tolist()],
            anns_field="embedding",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=top_k * 3,
            output_fields=["chunk_id", "doc_id", "text", "metadata_json"],
        )
        chunks: list[ScoredChunk] = []
        for hit in results[0]:
            metadata = json.loads(hit.entity.get("metadata_json") or "{}")
            if not match_filters(metadata, filters):
                continue
            chunks.append(
                ScoredChunk(
                    id=hit.entity.get("chunk_id"),
                    text=hit.entity.get("text"),
                    metadata=metadata,
                    score=float(hit.score),
                )
            )
        return chunks[:top_k]

    async def delete(self, doc_id: str) -> int:
        collection = self._get_collection()
        expr = f'doc_id == "{doc_id}"'
        collection.delete(expr)
        collection.flush()
        return 0

    async def list_documents(self) -> list[dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        rows = collection.query(expr='doc_id != ""', output_fields=["doc_id", "metadata_json"])
        docs: dict[str, dict[str, Any]] = {}
        for row in rows:
            metadata = json.loads(row.get("metadata_json") or "{}")
            doc_id = row.get("doc_id", "unknown")
            doc = docs.setdefault(
                doc_id,
                {
                    "doc_id": doc_id,
                    "doc_title": metadata.get("doc_title", ""),
                    "doc_type": metadata.get("doc_type", ""),
                    "chunk_count": 0,
                    "metadata": {},
                },
            )
            doc["chunk_count"] += 1
            doc["metadata"].update(metadata)
        return list(docs.values())

    async def clear(self) -> int:
        pymilvus = self._pymilvus
        if pymilvus.utility.has_collection(self.collection_name):
            pymilvus.utility.drop_collection(self.collection_name)
        self._collection = None
        return 0

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        pymilvus = self._pymilvus
        pymilvus.connections.connect(host=self.host, port=str(self.port))
        if not pymilvus.utility.has_collection(self.collection_name):
            fields = [
                pymilvus.FieldSchema(name="chunk_id", dtype=pymilvus.DataType.VARCHAR, max_length=128, is_primary=True),
                pymilvus.FieldSchema(name="doc_id", dtype=pymilvus.DataType.VARCHAR, max_length=128),
                pymilvus.FieldSchema(name="text", dtype=pymilvus.DataType.VARCHAR, max_length=8192),
                pymilvus.FieldSchema(name="metadata_json", dtype=pymilvus.DataType.VARCHAR, max_length=4096),
                pymilvus.FieldSchema(name="embedding", dtype=pymilvus.DataType.FLOAT_VECTOR, dim=self.dim),
            ]
            schema = pymilvus.CollectionSchema(fields=fields, description="Vehicle-RAG chunks")
            collection = pymilvus.Collection(self.collection_name, schema)
            collection.create_index(
                "embedding",
                {"index_type": "IVF_FLAT", "metric_type": "IP", "params": {"nlist": 128}},
            )
        else:
            collection = pymilvus.Collection(self.collection_name)
        self._collection = collection
        return collection

    def _load_pymilvus(self):
        try:
            import pymilvus
        except ImportError as exc:
            raise RuntimeError("Install pymilvus to use MilvusVectorStore.") from exc
        return pymilvus
