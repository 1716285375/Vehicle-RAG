from app.ingestion.splitters.heading_splitter import HeadingSplitter
from app.ingestion.splitters.semantic_splitter import FAQSplitter, TroubleCodeSplitter
from app.ingestion.splitters.strategy import SplitterRouter
from app.models import Page


def test_heading_splitter_keeps_heading_path():
    pages = [Page(page_number=1, text="# 驾驶\n\n## AUTOHOLD\n车辆静止时按下 AUTOHOLD 按键。")]
    chunks = HeadingSplitter().split(pages, {"doc_id": "d1", "doc_title": "手册"})
    assert chunks
    assert chunks[-1].metadata["heading_path"] == ["驾驶", "AUTOHOLD"]


def test_faq_splitter_pairs_question_and_answer():
    pages = [Page(page_number=1, text="Q: 首保多久?\n\nA: 以手册说明为准。")]
    chunks = FAQSplitter().split(pages, {"doc_id": "d1"})
    assert len(chunks) == 1
    assert "首保" in chunks[0].text


def test_trouble_code_splitter_sets_code():
    pages = [Page(page_number=1, text="P0301 | 第1缸失火 | 检查点火系统")]
    chunks = TroubleCodeSplitter().split(pages, {"doc_id": "d1"})
    assert chunks[0].metadata["code"] == "P0301"


def test_splitter_router_rejects_unknown_doc_type():
    try:
        SplitterRouter().get("unknown")
    except ValueError as exc:
        assert "Unsupported doc_type" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
