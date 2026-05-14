import argparse
import asyncio
import json
from pathlib import Path

from app.retrieval.json_store import JsonVectorStore


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--index-path", default=None, help="Optional JSON index path")
    args = parser.parse_args()

    store = JsonVectorStore(Path(args.index_path) if args.index_path else None)
    rows = await store.export_chunks()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"chunks": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"exported": len(rows), "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
