import json

from app.llm.client import build_chat_messages, parse_openai_sse_token


def test_parse_openai_sse_token_extracts_delta_content():
    line = "data: " + json.dumps({"choices": [{"delta": {"content": "AUTOHOLD"}}]})
    assert parse_openai_sse_token(line) == "AUTOHOLD"


def test_parse_openai_sse_token_ignores_done_marker():
    assert parse_openai_sse_token("data: [DONE]") is None


def test_build_chat_messages_includes_context_and_question():
    messages = build_chat_messages("AUTOHOLD 怎么开", "[1] 按下 AUTOHOLD。")
    assert messages[0]["role"] == "system"
    assert "AUTOHOLD 怎么开" in messages[1]["content"]
    assert "[1] 按下 AUTOHOLD。" in messages[1]["content"]
