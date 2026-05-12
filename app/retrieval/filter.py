from typing import Any


def match_filters(metadata: dict[str, Any], filters: dict[str, Any] | None) -> bool:
    if not filters:
        return True
    for key, expected in filters.items():
        if expected is None:
            continue
        actual = metadata.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True

