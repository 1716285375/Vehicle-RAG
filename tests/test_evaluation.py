from app.qa.evaluation import score_item, summarize_scores


def test_score_item_checks_expected_doc_and_keywords():
    result = {
        "answer": "AUTOHOLD 可以通过中控按键打开。",
        "citations": [{"doc_id": "manual-1"}],
    }
    score = score_item(
        {"expected_doc_id": "manual-1", "expected_keywords": ["AUTOHOLD", "中控"]},
        result,
    )
    assert score == {"citation_hit": True, "keyword_hit": True}


def test_summarize_scores_computes_rates():
    summary = summarize_scores(
        [
            {"citation_hit": True, "keyword_hit": True},
            {"citation_hit": False, "keyword_hit": True},
        ]
    )
    assert summary.as_dict()["citation_hit_rate"] == 0.5
    assert summary.as_dict()["keyword_hit_rate"] == 1.0
