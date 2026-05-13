import argparse
import asyncio
import json

from app.ingestion.doc_types import SUPPORTED_DOC_TYPES
from app.ingestion.rebuild import ingest_directory, rebuild_index


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Directory containing source documents")
    parser.add_argument("--doc-type", required=True, choices=SUPPORTED_DOC_TYPES)
    parser.add_argument("--metadata", default="{}")
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    if args.clear:
        result = await rebuild_index(args.dir, args.doc_type, json.loads(args.metadata))
    else:
        result = await ingest_directory(args.dir, args.doc_type, json.loads(args.metadata))
    for document in result["documents"]:
        print(json.dumps(document, ensure_ascii=False))
    print(json.dumps({"summary": result}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
