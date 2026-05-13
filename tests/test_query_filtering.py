import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.models import Chunk
from app.qa.chain import RAGChain
from app.retrieval import JsonVectorStore


def test_qa_chain_uses_inferred_trouble_code_filter(tmp_path: Path):
    asyncio.run(_run_qa_chain_uses_inferred_trouble_code_filter(tmp_path))


async def _run_qa_chain_uses_inferred_trouble_code_filter(tmp_path: Path):
    embedder = HashEmbedder(dim=64)
    store = JsonVectorStore(tmp_path / "index.json")
    chunks = [
        Chunk(
            text="P0301 表示第1缸失火。",
            metadata={"doc_id": "codes", "doc_title": "故障码表", "code": "P0301"},
            embedding=await embedder.embed("P0301 表示第1缸失火。"),
        ),
        Chunk(
            text="P0420 表示催化器系统效率低。",
            metadata={"doc_id": "codes", "doc_title": "故障码表", "code": "P0420"},
            embedding=await embedder.embed("P0420 表示催化器系统效率低。"),
        ),
    ]
    await store.upsert(chunks)

    result = await RAGChain(embedder=embedder, vector_store=store).answer("P0301 是什么意思")

    assert "P0301" in result["answer"]
    assert result["citations"][0]["text"].startswith("P0301")
