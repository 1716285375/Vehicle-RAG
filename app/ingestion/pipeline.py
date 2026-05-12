from pathlib import Path
from typing import Any
from uuid import uuid4

from app.embedding import HashEmbedder
from app.ingestion.cleaners import DocumentCleaner
from app.ingestion.loaders import LoaderFactory
from app.ingestion.splitters import SplitterRouter
from app.retrieval import JsonVectorStore


class IngestionPipeline:
    def __init__(
        self,
        loader_factory: LoaderFactory | None = None,
        cleaner: DocumentCleaner | None = None,
        splitter_router: SplitterRouter | None = None,
        embedder: HashEmbedder | None = None,
        vector_store: JsonVectorStore | None = None,
    ) -> None:
        self.loader_factory = loader_factory or LoaderFactory()
        self.cleaner = cleaner or DocumentCleaner()
        self.splitter_router = splitter_router or SplitterRouter()
        self.embedder = embedder or HashEmbedder()
        self.vector_store = vector_store or JsonVectorStore()

    async def ingest(
        self, file_path: str | Path, doc_type: str, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        path = Path(file_path)
        metadata = dict(metadata or {})
        doc_id = str(metadata.get("doc_id") or uuid4())
        base_metadata = {
            **metadata,
            "doc_id": doc_id,
            "doc_title": metadata.get("doc_title") or path.stem,
            "doc_type": doc_type,
            "source": str(path),
        }
        loader = self.loader_factory.get(path)
        pages = await loader.load(path)
        cleaned = self.cleaner.clean(pages)
        chunks = self.splitter_router.get(doc_type).split(cleaned, base_metadata)
        embeddings = await self.embedder.embed_batch([chunk.text for chunk in chunks])
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        await self.vector_store.upsert(chunks)
        return {"doc_id": doc_id, "ingested": len(chunks), "doc_title": base_metadata["doc_title"]}

