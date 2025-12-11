import json
from typing import Any

import redis.asyncio as redis

from src.domain.ports import Cache
from src.core import settings


class RedisCache(Cache):

    def __init__(self, url: str | None = None):
        self._url = url or settings.redis_url
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        if self._client is None:
            self._client = redis.from_url(self._url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def get(self, key: str) -> Any | None:
        if not self._client:
            await self.connect()

        value = await self._client.get(key)

        if value:
            return json.loads(value)

        return None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        if not self._client:
            await self.connect()

        serialized = json.dumps(value)
        ttl = ttl_seconds or settings.cache_ttl_seconds

        await self._client.setex(key, ttl, serialized)

    async def delete(self, key: str) -> None:
        if not self._client:
            await self.connect()

        await self._client.delete(key)

