from app.qa.prompt_templates import build_qa_messages, render_template


def test_render_template_substitutes_values():
    rendered = render_template("qa.tmpl", context="[1] 内容", question="AUTOHOLD 怎么开")
    assert "[1] 内容" in rendered
    assert "AUTOHOLD 怎么开" in rendered


def test_build_qa_messages_uses_prompt_files():
    messages = build_qa_messages("P0301 是什么", "[1] P0301 表示第1缸失火")
    assert messages[0]["role"] == "system"
    assert "仅基于" in messages[0]["content"]
    assert messages[1]["role"] == "user"
    assert "P0301 是什么" in messages[1]["content"]
