from app.models import Citation
from app.qa.citation import bind_answer_citations, extract_citation_ids


def test_extract_citation_ids_from_answer():
    assert extract_citation_ids("打开 AUTOHOLD [2], 也可参考 [10]。") == {2, 10}


def test_bind_answer_citations_returns_only_referenced_sources():
    citations = [
        Citation(id=1, doc_id="d1", doc_title="Manual", section="A", text="one", score=0.9),
        Citation(id=2, doc_id="d2", doc_title="FAQ", section="B", text="two", score=0.8),
    ]

    bound = bind_answer_citations("答案引用 [2]", citations)
    assert [citation.id for citation in bound] == [2]


def test_bind_answer_citations_returns_empty_without_references():
    citations = [Citation(id=1, doc_id="d1", doc_title="Manual", section="A", text="one", score=0.9)]
    assert bind_answer_citations("没有引用编号", citations) == []
