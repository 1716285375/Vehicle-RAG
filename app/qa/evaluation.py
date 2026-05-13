from dataclasses import dataclass
from typing import Any


@dataclass
class EvaluationResult:
    total: int = 0
    citation_hit: int = 0
    keyword_hit: int = 0

    @property
    def citation_hit_rate(self) -> float:
        return self.citation_hit / self.total if self.total else 0.0

    @property
    def keyword_hit_rate(self) -> float:
        return self.keyword_hit / self.total if self.total else 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "citation_hit": self.citation_hit,
            "citation_hit_rate": round(self.citation_hit_rate, 4),
            "keyword_hit": self.keyword_hit,
            "keyword_hit_rate": round(self.keyword_hit_rate, 4),
        }


def score_item(expected: dict[str, Any], result: dict[str, Any]) -> dict[str, bool]:
    citations = result.get("citations", [])
    answer = result.get("answer", "")
    expected_doc_id = expected.get("expected_doc_id")
    expected_keywords = expected.get("expected_keywords") or []

    citation_hit = True
    if expected_doc_id:
        citation_hit = any(citation.get("doc_id") == expected_doc_id for citation in citations)

    keyword_hit = True
    if expected_keywords:
        keyword_hit = all(keyword in answer for keyword in expected_keywords)

    return {"citation_hit": citation_hit, "keyword_hit": keyword_hit}


def summarize_scores(scores: list[dict[str, bool]]) -> EvaluationResult:
    summary = EvaluationResult(total=len(scores))
    for score in scores:
        summary.citation_hit += int(score.get("citation_hit", False))
        summary.keyword_hit += int(score.get("keyword_hit", False))
    return summary
