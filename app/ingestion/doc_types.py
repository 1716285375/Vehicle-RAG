SUPPORTED_DOC_TYPES = ("manual", "faq", "trouble_code", "policy")


def validate_doc_type(doc_type: str) -> str:
    normalized = doc_type.strip().lower()
    if normalized not in SUPPORTED_DOC_TYPES:
        allowed = ", ".join(SUPPORTED_DOC_TYPES)
        raise ValueError(f"Unsupported doc_type '{doc_type}'. Expected one of: {allowed}")
    return normalized
