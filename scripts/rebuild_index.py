import argparse
import asyncio
import json
from pathlib import Path

from app.config.settings import settings
from app.ingestion.doc_types import SUPPORTED_DOC_TYPES
from app.ingestion.pipeline import IngestionPipeline


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Directory containing source documents")
    parser.add_argument("--doc-type", required=True, choices=SUPPORTED_DOC_TYPES)
    parser.add_argument("--metadata", default="{}")
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    if args.clear and settings.index_path.exists():
        settings.index_path.unlink()

    pipeline = IngestionPipeline()
    base_metadata = json.loads(args.metadata)
    supported = {".pdf", ".docx", ".md", ".markdown", ".txt", ".html", ".htm"}
    for path in sorted(Path(args.dir).rglob("*")):
        if not path.is_file() or path.suffix.lower() not in supported:
            continue
        result = await pipeline.ingest(path, args.doc_type, {**base_metadata, "doc_title": path.stem})
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
