import redis.asyncio as redis


# абстрактный класс
class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.redis = None

    async def connect(self):
        self.redis = await redis.Redis(
            host=self.host, port=self.port, decode_responses=True
        )

    async def set(self, key: str, value: str, expire: int = None):
        if expire:
            await self.redis.set(key, value, ex=expire)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str):
        return await self.redis.get(key)

    async def ttl(self, key: str) -> int:
        """
        Возвращает оставшееся время жизни ключа в секундах.
        - Вернёт -2, если ключа нет
        - Вернёт -1, если TTL не установлен
        """
        return await self.redis.ttl(key)

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
