import argparse
import asyncio
import json
from pathlib import Path

from app.qa.chain import RAGChain


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="JSONL with question and optional filters")
    args = parser.parse_args()
    chain = RAGChain()
    for line in Path(args.file).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        result = await chain.answer(item["question"], item.get("filters"))
        print(json.dumps({"question": item["question"], **result}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())

