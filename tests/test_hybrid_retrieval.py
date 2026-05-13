import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.models import Chunk
from app.retrieval import JsonVectorStore
from app.retrieval.hybrid import bm25_scores


def test_bm25_scores_exact_fault_code_match_highest():
    scores = bm25_scores("P0301 是什么故障", ["P0301 第1缸失火", "P0420 催化器效率低"])
    assert scores[0] > scores[1]


def test_json_store_hybrid_search_uses_query_text(tmp_path: Path):
    asyncio.run(_run_json_store_hybrid_search_uses_query_text(tmp_path))


async def _run_json_store_hybrid_search_uses_query_text(tmp_path: Path):
    embedder = HashEmbedder(dim=64)
    chunks = [
        Chunk(
            text="P0420 催化器系统效率低。",
            metadata={"doc_id": "d1", "code": "P0420"},
            embedding=await embedder.embed("P0420 催化器系统效率低。"),
        ),
        Chunk(
            text="P0301 表示第1缸失火。",
            metadata={"doc_id": "d2", "code": "P0301"},
            embedding=await embedder.embed("无关文本"),
        ),
    ]
    store = JsonVectorStore(tmp_path / "index.json")
    await store.upsert(chunks)

    results = await store.search(
        await embedder.embed("P0420 催化器系统效率低。"),
        top_k=2,
        query_text="P0301 是什么故障",
    )
    assert results[0].metadata["code"] == "P0301"
