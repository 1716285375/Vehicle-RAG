import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.models import Chunk
from app.retrieval.faiss_store import FaissVectorStore


def test_faiss_store_search_delete_and_list(tmp_path: Path):
    asyncio.run(_run_faiss_store_search_delete_and_list(tmp_path))


async def _run_faiss_store_search_delete_and_list(tmp_path: Path):
    embedder = HashEmbedder(dim=64)
    store = FaissVectorStore(tmp_path / "vehicle.faiss")
    chunk = Chunk(
        text="P0301 表示第1缸失火,建议检查点火系统。",
        metadata={"doc_id": "codes", "doc_title": "故障码表", "doc_type": "trouble_code", "code": "P0301"},
        embedding=await embedder.embed("P0301 表示第1缸失火,建议检查点火系统。"),
    )
    await store.upsert([chunk])

    docs = await store.list_documents()
    assert docs[0]["doc_id"] == "codes"
    assert docs[0]["chunk_count"] == 1

    results = await store.search(await embedder.embed("P0301 是什么故障"), 5, {"code": "P0301"})
    assert results
    assert results[0].metadata["code"] == "P0301"

    deleted = await store.delete("codes")
    assert deleted == 1
    assert await store.search(await embedder.embed("P0301 是什么故障"), 5) == []
