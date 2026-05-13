from fastapi import HTTPException

from app.api.ingest import parse_metadata


def test_parse_metadata_accepts_empty_value():
    assert parse_metadata("") == {}


def test_parse_metadata_rejects_invalid_json():
    try:
        parse_metadata("{bad")
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "Invalid metadata JSON" in exc.detail
    else:
        raise AssertionError("Expected HTTPException")


def test_parse_metadata_rejects_non_object_json():
    try:
        parse_metadata("[]")
    except HTTPException as exc:
        assert exc.status_code == 422
        assert "metadata must be a JSON object" in exc.detail
    else:
        raise AssertionError("Expected HTTPException")
