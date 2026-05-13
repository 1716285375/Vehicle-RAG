import argparse
import asyncio
import json
from pathlib import Path

from app.qa.evaluation import score_item, summarize_scores
from app.qa.chain import RAGChain


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="JSONL with question and optional filters")
    parser.add_argument("--summary-only", action="store_true", help="Only print aggregate metrics")
    args = parser.parse_args()
    chain = RAGChain()
    scores = []
    for line in Path(args.file).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        result = await chain.answer(item["question"], item.get("filters"))
        score = score_item(item, result)
        scores.append(score)
        if not args.summary_only:
            print(json.dumps({"question": item["question"], "score": score, **result}, ensure_ascii=False))
    print(json.dumps({"summary": summarize_scores(scores).as_dict()}, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
