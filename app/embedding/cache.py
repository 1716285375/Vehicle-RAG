import hashlib


def text_cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

