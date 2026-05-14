import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.ingestion.pipeline import IngestionPipeline
from app.qa.chain import RAGChain
from app.retrieval import JsonVectorStore


def test_retrieve_debug_returns_reranked_candidates(tmp_path: Path):
    asyncio.run(_run_retrieve_debug_returns_reranked_candidates(tmp_path))


async def _run_retrieve_debug_returns_reranked_candidates(tmp_path: Path):
    source = tmp_path / "manual.md"
    source.write_text("# 驾驶\n\n## AUTOHOLD\n车辆静止时按下 AUTOHOLD 按键。", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    embedder = HashEmbedder(dim=64)
    await IngestionPipeline(embedder=embedder, vector_store=store).ingest(
        source, "manual", {"doc_id": "manual-debug", "vehicle_model": "L9"}
    )

    result = await RAGChain(embedder=embedder, vector_store=store).retrieve_debug(
        "L9 AUTOHOLD 怎么开"
    )

    assert result["rewritten"]
    assert result["filters"]["vehicle_model"] == "L9"
    assert result["candidates"]
    assert "AUTOHOLD" in result["candidates"][0]["text"]
