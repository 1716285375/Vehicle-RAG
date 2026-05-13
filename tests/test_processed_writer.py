import asyncio
import json
from pathlib import Path

from app.embedding import HashEmbedder
from app.ingestion.pipeline import IngestionPipeline
from app.ingestion.processed_writer import ProcessedChunkWriter
from app.retrieval import JsonVectorStore


def test_ingestion_writes_processed_chunks(tmp_path: Path):
    asyncio.run(_run_ingestion_writes_processed_chunks(tmp_path))


async def _run_ingestion_writes_processed_chunks(tmp_path: Path):
    source = tmp_path / "manual.md"
    source.write_text("# 驾驶\n\n## AUTOHOLD\n车辆静止时按下 AUTOHOLD 按键。", encoding="utf-8")
    writer = ProcessedChunkWriter(tmp_path / "processed")
    result = await IngestionPipeline(
        embedder=HashEmbedder(dim=64),
        vector_store=JsonVectorStore(tmp_path / "index.json"),
        processed_writer=writer,
    ).ingest(source, "manual", {"doc_id": "manual-processed"})

    processed_path = Path(result["processed_path"])
    assert processed_path.exists()
    row = json.loads(processed_path.read_text(encoding="utf-8").splitlines()[0])
    assert row["metadata"]["doc_id"] == "manual-processed"
    assert "embedding" not in row
