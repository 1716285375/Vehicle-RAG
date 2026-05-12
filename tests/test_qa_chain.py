from pathlib import Path
import asyncio

from app.embedding import HashEmbedder
from app.ingestion.pipeline import IngestionPipeline
from app.qa.chain import RAGChain
from app.retrieval import JsonVectorStore


def test_qa_chain_answers_with_citation(tmp_path: Path):
    asyncio.run(_run_qa_chain_answers_with_citation(tmp_path))


async def _run_qa_chain_answers_with_citation(tmp_path: Path):
    source = tmp_path / "manual.md"
    source.write_text("# 驾驶\n\n## AUTOHOLD\n车辆静止时按下 AUTOHOLD 按键,指示灯亮起即启用。", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    embedder = HashEmbedder(dim=64)
    await IngestionPipeline(embedder=embedder, vector_store=store).ingest(
        source, "manual", {"vehicle_model": "L9", "doc_id": "manual-1"}
    )

    result = await RAGChain(embedder=embedder, vector_store=store).answer(
        "AUTOHOLD 怎么打开", {"vehicle_model": "L9"}
    )
    assert "AUTOHOLD" in result["answer"]
    assert result["citations"]
