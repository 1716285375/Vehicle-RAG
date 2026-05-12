import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.ingestion.pipeline import IngestionPipeline
from app.qa.chain import RAGChain
from app.retrieval import JsonVectorStore


class LowScoreReranker:
    async def rerank(self, query, candidates, top_k=5):
        for candidate in candidates:
            candidate.rerank_score = 0.0
        return candidates[:top_k]


def test_qa_chain_falls_back_when_relevance_is_low(tmp_path: Path):
    asyncio.run(_run_qa_chain_falls_back_when_relevance_is_low(tmp_path))


async def _run_qa_chain_falls_back_when_relevance_is_low(tmp_path: Path):
    source = tmp_path / "manual.md"
    source.write_text("# 驾驶\n\n## AUTOHOLD\n车辆静止时按下 AUTOHOLD 按键。", encoding="utf-8")
    store = JsonVectorStore(tmp_path / "index.json")
    embedder = HashEmbedder(dim=64)
    await IngestionPipeline(embedder=embedder, vector_store=store).ingest(
        source, "manual", {"vehicle_model": "L9", "doc_id": "manual-low-score"}
    )

    result = await RAGChain(
        embedder=embedder,
        vector_store=store,
        reranker=LowScoreReranker(),
    ).answer("低置信度测试问题", {"vehicle_model": "L9"})

    assert "知识库中暂未找到相关信息" in result["answer"]
    assert result["citations"] == []
