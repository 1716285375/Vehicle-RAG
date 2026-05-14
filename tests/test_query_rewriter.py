import asyncio

from app.qa.query_rewriter import QueryRewriter


class FakeRewriteLLM:
    async def generate(self, question: str, context: str) -> str:
        assert "请将用户问题改写" in question
        return "如何启用 AUTOHOLD 自动驻车功能"


def test_query_rewriter_applies_local_synonyms():
    asyncio.run(_run_query_rewriter_applies_local_synonyms())


async def _run_query_rewriter_applies_local_synonyms():
    rewritten = await QueryRewriter(enable_llm=False).rewrite("autohold 怎么开")
    assert "AUTOHOLD 自动驻车" in rewritten


def test_query_rewriter_uses_llm_when_enabled():
    asyncio.run(_run_query_rewriter_uses_llm_when_enabled())


async def _run_query_rewriter_uses_llm_when_enabled():
    rewritten = await QueryRewriter(llm=FakeRewriteLLM(), enable_llm=True).rewrite("怎么开自动驻车")
    assert rewritten == "如何启用 AUTOHOLD 自动驻车功能"
