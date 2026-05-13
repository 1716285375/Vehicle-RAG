from app.api.knowledge import _matches_document


def test_matches_document_uses_metadata_filters():
    document = {
        "doc_id": "manual-1",
        "doc_type": "manual",
        "metadata": {"vehicle_model": "L9"},
    }

    assert _matches_document(document, {"doc_type": "manual", "vehicle_model": "L9"})
    assert not _matches_document(document, {"doc_type": "faq", "vehicle_model": "L9"})
    assert not _matches_document(document, {"doc_type": "manual", "vehicle_model": "L8"})
