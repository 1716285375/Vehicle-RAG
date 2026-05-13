import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.rebuild import ingest_directory, rebuild_index
from app.retrieval import JsonVectorStore


def test_ingest_directory_summarizes_documents(tmp_path: Path):
    asyncio.run(_run_ingest_directory_summarizes_documents(tmp_path))


async def _run_ingest_directory_summarizes_documents(tmp_path: Path):
    docs_dir = tmp_path / "raw"
    docs_dir.mkdir()
    (docs_dir / "manual.md").write_text("# 驾驶\n\n## AUTOHOLD\n按下 AUTOHOLD。", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    pipeline = IngestionPipeline(embedder=HashEmbedder(dim=64), vector_store=store)

    result = await ingest_directory(docs_dir, "manual", {"vehicle_model": "L9"}, pipeline)

    assert result["document_count"] == 1
    assert result["chunk_count"] >= 1


def test_rebuild_index_clears_existing_chunks(tmp_path: Path):
    asyncio.run(_run_rebuild_index_clears_existing_chunks(tmp_path))


async def _run_rebuild_index_clears_existing_chunks(tmp_path: Path):
    docs_dir = tmp_path / "raw"
    docs_dir.mkdir()
    (docs_dir / "manual.md").write_text("# 驾驶\n\n## AUTOHOLD\n按下 AUTOHOLD。", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    await IngestionPipeline(embedder=HashEmbedder(dim=64), vector_store=store).ingest(
        docs_dir / "manual.md", "manual", {"doc_id": "old"}
    )

    result = await rebuild_index(docs_dir, "manual", {"vehicle_model": "L9"}, store)

    assert result["deleted_chunks"] >= 1
    docs = await store.list_documents()
    assert len(docs) == 1


def test_rebuild_index_validates_doc_type_before_clear(tmp_path: Path):
    asyncio.run(_run_rebuild_index_validates_doc_type_before_clear(tmp_path))


async def _run_rebuild_index_validates_doc_type_before_clear(tmp_path: Path):
    docs_dir = tmp_path / "raw"
    docs_dir.mkdir()
    (docs_dir / "manual.md").write_text("# 驾驶\n\n内容", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    await IngestionPipeline(embedder=HashEmbedder(dim=64), vector_store=store).ingest(
        docs_dir / "manual.md", "manual", {"doc_id": "existing"}
    )

    try:
        await rebuild_index(docs_dir, "bad_type", {}, store)
    except ValueError as exc:
        assert "Unsupported doc_type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    docs = await store.list_documents()
    assert docs[0]["doc_id"] == "existing"
