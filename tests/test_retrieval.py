from pathlib import Path
import asyncio

from app.embedding import HashEmbedder
from app.models import Chunk
from app.retrieval import JsonVectorStore


def test_json_vector_store_search_with_filters(tmp_path: Path):
    asyncio.run(_run_json_vector_store_search_with_filters(tmp_path))


async def _run_json_vector_store_search_with_filters(tmp_path: Path):
    embedder = HashEmbedder(dim=64)
    chunk = Chunk(
        text="AUTOHOLD 自动驻车按键在中控台。",
        metadata={"doc_id": "d1", "vehicle_model": "L9"},
        embedding=await embedder.embed("AUTOHOLD 自动驻车按键在中控台。"),
    )
    store = JsonVectorStore(tmp_path / "index.json")
    await store.upsert([chunk])

    results = await store.search(await embedder.embed("AUTOHOLD 怎么开"), 5, {"vehicle_model": "L9"})
    assert results
    assert results[0].metadata["doc_id"] == "d1"

    empty = await store.search(await embedder.embed("AUTOHOLD 怎么开"), 5, {"vehicle_model": "L8"})
    assert empty == []


def test_json_vector_store_clear_removes_chunks(tmp_path: Path):
    asyncio.run(_run_json_vector_store_clear_removes_chunks(tmp_path))


async def _run_json_vector_store_clear_removes_chunks(tmp_path: Path):
    embedder = HashEmbedder(dim=64)
    store = JsonVectorStore(tmp_path / "index.json")
    await store.upsert(
        [
            Chunk(
                text="AUTOHOLD 自动驻车按键在中控台。",
                metadata={"doc_id": "d1"},
                embedding=await embedder.embed("AUTOHOLD 自动驻车按键在中控台。"),
            )
        ]
    )
    assert await store.clear() == 1
    assert await store.list_documents() == []
