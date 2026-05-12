class NullCache:
    async def get(self, key: str) -> str | None:
        return None

    async def setex(self, key: str, ttl: int, value: str) -> None:
        return None


cache = NullCache()

