import json
from collections.abc import AsyncIterator

import httpx

from app.config.settings import settings


def build_chat_messages(question: str, context: str) -> list[dict[str, str]]:
    prompt = f"【参考资料】\n{context}\n\n【用户问题】\n{question}\n\n【回答】"
    return [
        {"role": "system", "content": "你是车载智能助手,只能基于参考资料回答。"},
        {"role": "user", "content": prompt},
    ]


def parse_openai_sse_token(line: str) -> str | None:
    line = line.strip()
    if not line.startswith("data:"):
        return None
    payload = line.removeprefix("data:").strip()
    if not payload or payload == "[DONE]":
        return None
    data = json.loads(payload)
    choices = data.get("choices") or []
    if not choices:
        return None
    delta = choices[0].get("delta") or {}
    return delta.get("content")


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
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            response = await client.post(
                settings.llm_base_url.rstrip("/") + "/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": build_chat_messages(question, context),
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, question: str, context: str) -> AsyncIterator[str]:
        if not settings.llm_base_url or not settings.llm_api_key:
            async for char in ExtractiveLLM().stream(question, context):
                yield char
            return

        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            async with client.stream(
                "POST",
                settings.llm_base_url.rstrip("/") + "/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": build_chat_messages(question, context),
                    "temperature": 0.2,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    token = parse_openai_sse_token(line)
                    if token:
                        yield token
