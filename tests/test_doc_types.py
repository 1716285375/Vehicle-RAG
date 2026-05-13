from app.ingestion.doc_types import validate_doc_type


def test_validate_doc_type_normalizes_supported_type():
    assert validate_doc_type(" Manual ") == "manual"


def test_validate_doc_type_rejects_unknown_type():
    try:
        validate_doc_type("unknown")
    except ValueError as exc:
        assert "Unsupported doc_type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
