from pathlib import Path
from typing import Any

from app.ingestion.pipeline import IngestionPipeline
from app.retrieval import VectorStore, build_vector_store

SUPPORTED_SOURCE_SUFFIXES = {".pdf", ".docx", ".md", ".markdown", ".txt", ".html", ".htm"}


async def ingest_directory(
    directory: str | Path,
    doc_type: str,
    metadata: dict[str, Any] | None = None,
    pipeline: IngestionPipeline | None = None,
) -> dict[str, Any]:
    root = Path(directory)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Directory does not exist: {root}")

    pipeline = pipeline or IngestionPipeline()
    base_metadata = dict(metadata or {})
    results: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES:
            continue
        result = await pipeline.ingest(path, doc_type, {**base_metadata, "doc_title": path.stem})
        results.append(result)
    return {
        "directory": str(root),
        "doc_type": doc_type,
        "documents": results,
        "document_count": len(results),
        "chunk_count": sum(item.get("ingested", 0) for item in results),
    }


async def rebuild_index(
    directory: str | Path,
    doc_type: str,
    metadata: dict[str, Any] | None = None,
    vector_store: VectorStore | None = None,
) -> dict[str, Any]:
    store = vector_store or build_vector_store()
    deleted_chunks = await store.clear()
    pipeline = IngestionPipeline(vector_store=store)
    result = await ingest_directory(directory, doc_type, metadata, pipeline)
    return {"deleted_chunks": deleted_chunks, **result}
