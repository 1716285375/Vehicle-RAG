import asyncio
from pathlib import Path

from app.embedding import HashEmbedder
from app.models import Chunk
from app.retrieval.json_store import JsonVectorStore


def test_json_store_exports_and_imports_chunks(tmp_path: Path):
    asyncio.run(_run_json_store_exports_and_imports_chunks(tmp_path))


async def _run_json_store_exports_and_imports_chunks(tmp_path: Path):
    embedder = HashEmbedder(dim=64)
    source = JsonVectorStore(tmp_path / "source.json")
    chunk = Chunk(
        text="AUTOHOLD 自动驻车",
        metadata={"doc_id": "manual-1"},
        embedding=await embedder.embed("AUTOHOLD 自动驻车"),
    )
    await source.upsert([chunk])

    rows = await source.export_chunks()
    target = JsonVectorStore(tmp_path / "target.json")
    imported = await target.import_chunks(rows, replace=True)

    assert imported == 1
    assert (await target.list_documents())[0]["doc_id"] == "manual-1"
