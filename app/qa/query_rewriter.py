from app.config.settings import settings
from app.qa.prompt_templates import render_template


class QueryRewriter:
    def __init__(self, llm=None, enable_llm: bool | None = None) -> None:
        self.llm = llm
        self.enable_llm = settings.enable_llm_query_rewrite if enable_llm is None else enable_llm

    async def rewrite(self, question: str) -> str:
        normalized = " ".join(question.strip().split())
        if self.enable_llm and self.llm is not None:
            rewritten = await self._rewrite_with_llm(normalized)
            if rewritten:
                return rewritten
        return self._rewrite_locally(normalized)

    def _rewrite_locally(self, question: str) -> str:
        synonyms = {
            "自动驻车": "AUTOHOLD 自动驻车",
            "autohold": "AUTOHOLD 自动驻车",
            "胎压": "胎压 胎压监测 胎压报警",
        }
        lowered = question.lower()
        for key, value in synonyms.items():
            if key in lowered and value not in question:
                return f"{question} {value}"
        return question

    async def _rewrite_with_llm(self, question: str) -> str:
        prompt = render_template("rewrite.tmpl", question=question)
        rewritten = await self.llm.generate(prompt, "")
        rewritten = " ".join(rewritten.strip().split())
        return rewritten or question
