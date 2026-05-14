from app.models import ScoredChunk
from app.qa.citation import ContextBuilder, truncate_to_token_budget


def test_truncate_to_token_budget_shortens_long_text():
    text = "A" * 200
    truncated = truncate_to_token_budget(text, 20)
    assert len(truncated) <= 40
    assert truncated.endswith("…")


def test_context_builder_truncates_chunk_to_budget():
    chunk = ScoredChunk(
        text="AUTOHOLD " * 100,
        metadata={"doc_id": "d1", "doc_title": "Manual", "section": "AUTOHOLD"},
        score=1.0,
    )
    context, citations = ContextBuilder().build([chunk], max_tokens=30, min_chunk_tokens=10)

    assert "[1]" in context
    assert len(citations) == 1
    assert citations[0].text.endswith("…")
    assert len(citations[0].text) < len(chunk.text)


def test_context_builder_skips_chunk_when_remaining_budget_is_too_small():
    chunks = [
        ScoredChunk(text="A" * 80, metadata={"doc_id": "d1"}, score=1.0),
        ScoredChunk(text="B" * 80, metadata={"doc_id": "d2"}, score=0.9),
    ]
    _, citations = ContextBuilder().build(chunks, max_tokens=45, min_chunk_tokens=20)

    assert [citation.doc_id for citation in citations] == ["d1"]
