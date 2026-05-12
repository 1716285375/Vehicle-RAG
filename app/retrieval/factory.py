from app.config.settings import settings
from app.retrieval.faiss_store import FaissVectorStore
from app.retrieval.json_store import JsonVectorStore
from app.retrieval.milvus_store import MilvusVectorStore
from app.retrieval.vector_store import VectorStore


def build_vector_store(kind: str | None = None) -> VectorStore:
    backend = (kind or settings.vector_store).strip().lower()
    if backend == "json":
        return JsonVectorStore()
    if backend == "faiss":
        return FaissVectorStore()
    if backend == "milvus":
        return MilvusVectorStore()
    raise ValueError(f"Unsupported vector store backend: {backend}")
