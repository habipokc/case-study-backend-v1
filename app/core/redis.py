from typing import Optional
import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True
        )
        # Test connection
        await self.redis_client.ping()
        print("Redis connected successfully.")

    async def close(self):
        if self.redis_client:
            await self.redis_client.aclose()

    async def set_value(self, key: str, value: str, expire: int = None):
        if self.redis_client:
            await self.redis_client.set(key, value, ex=expire)

    async def get_value(self, key: str) -> Optional[str]:
        if self.redis_client:
            return await self.redis_client.get(key)
        return None
    
    async def delete_value(self, key: str):
        if self.redis_client:
            await self.redis_client.delete(key)

redis_client = RedisClient()
