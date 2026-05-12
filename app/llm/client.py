import json
from collections.abc import AsyncIterator

import httpx

from app.config.settings import settings


class ExtractiveLLM:
    async def generate(self, question: str, context: str) -> str:
        if not context.strip():
            return "抱歉,知识库中暂未找到相关信息,建议查阅车主手册或联系 4S 店。"
        first = context.split("\n", 1)[0]
        citation = "[1]" if first.startswith("[1]") else ""
        lines = [line.strip() for line in context.splitlines() if line.strip() and not line.startswith("[")]
        summary = lines[0] if lines else context[:160]
        return f"根据知识库资料,{summary} {citation}".strip()

    async def stream(self, question: str, context: str) -> AsyncIterator[str]:
        answer = await self.generate(question, context)
        for char in answer:
            yield char


class LLMClient:
    async def generate(self, question: str, context: str) -> str:
        if not settings.llm_base_url or not settings.llm_api_key:
            return await ExtractiveLLM().generate(question, context)
        prompt = f"【参考资料】\n{context}\n\n【用户问题】\n{question}\n\n【回答】"
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(
                settings.llm_base_url.rstrip("/") + "/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": [
                        {"role": "system", "content": "你是车载智能助手,只能基于参考资料回答。"},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, question: str, context: str) -> AsyncIterator[str]:
        # Keep streaming deterministic for the MVP; provider SSE can be added behind this method.
        answer = await self.generate(question, context)
        for char in answer:
            yield char

