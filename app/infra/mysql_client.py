class NullDatabase:
    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None


database = NullDatabase()

