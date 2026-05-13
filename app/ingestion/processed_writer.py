import json
from pathlib import Path

from app.config.settings import settings
from app.models import Chunk


class ProcessedChunkWriter:
    def __init__(self, output_dir: Path | None = None) -> None:
        self.output_dir = output_dir or settings.processed_dir / "chunks"

    def write(self, doc_id: str, chunks: list[Chunk]) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        path = self.output_dir / f"{doc_id}.jsonl"
        lines = []
        for chunk in chunks:
            payload = {
                "id": chunk.id,
                "text": chunk.text,
                "metadata": chunk.metadata,
            }
            lines.append(json.dumps(payload, ensure_ascii=False))
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return path
