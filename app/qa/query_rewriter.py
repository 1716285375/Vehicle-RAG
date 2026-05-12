class QueryRewriter:
    async def rewrite(self, question: str) -> str:
        normalized = " ".join(question.strip().split())
        synonyms = {
            "自动驻车": "AUTOHOLD 自动驻车",
            "autohold": "AUTOHOLD 自动驻车",
            "胎压": "胎压 胎压监测 胎压报警",
        }
        lowered = normalized.lower()
        for key, value in synonyms.items():
            if key in lowered and value not in normalized:
                return f"{normalized} {value}"
        return normalized

