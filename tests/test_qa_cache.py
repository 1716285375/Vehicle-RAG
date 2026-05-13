import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.infra.redis_client import InMemoryTTLCache
from app.ingestion.pipeline import IngestionPipeline
from app.qa.chain import RAGChain
from app.retrieval import JsonVectorStore


def test_qa_chain_marks_cached_answers(tmp_path: Path, monkeypatch):
    asyncio.run(_run_qa_chain_marks_cached_answers(tmp_path, monkeypatch))


async def _run_qa_chain_marks_cached_answers(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("app.qa.chain.cache", InMemoryTTLCache())
    source = tmp_path / "manual.md"
    source.write_text("# 驾驶\n\n## AUTOHOLD\n车辆静止时按下 AUTOHOLD 按键。", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    embedder = HashEmbedder(dim=64)
    await IngestionPipeline(embedder=embedder, vector_store=store).ingest(
        source, "manual", {"vehicle_model": "L9", "doc_id": "manual-cache"}
    )

    chain = RAGChain(embedder=embedder, vector_store=store)
    first = await chain.answer("AUTOHOLD 怎么打开", {"vehicle_model": "L9"})
    second = await chain.answer("AUTOHOLD 怎么打开", {"vehicle_model": "L9"})

    assert first["cached"] is False
    assert second["cached"] is True
    assert second["answer"] == first["answer"]
