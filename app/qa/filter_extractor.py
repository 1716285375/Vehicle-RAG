import re
from typing import Any

TROUBLE_CODE_RE = re.compile(r"\b([PBCU][0-9A-Fa-f]{4})\b")
VEHICLE_MODEL_RE = re.compile(r"\b([A-Z][0-9]{1,2})\b", re.IGNORECASE)


def extract_query_filters(question: str) -> dict[str, str]:
    filters: dict[str, str] = {}
    code_match = TROUBLE_CODE_RE.search(question)
    if code_match:
        filters["code"] = code_match.group(1).upper()

    model_match = VEHICLE_MODEL_RE.search(question)
    if model_match:
        model = model_match.group(1).upper()
        if model not in filters.values() and not TROUBLE_CODE_RE.fullmatch(model):
            filters["vehicle_model"] = model
    return filters


def merge_filters(explicit: dict[str, Any] | None, inferred: dict[str, str]) -> dict[str, Any]:
    merged = dict(inferred)
    merged.update(explicit or {})
    return merged
