from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings
import json
from typing import Any


class RedisClient:
    def __init__(self, url: str | None = None):
        self._url = url or settings.redis_url
        self._client = None

    def connect(self):
        if self._client is None:
            from redis.asyncio import from_url

            self._client = from_url(
                self._url,
                decode_responses=True,
                socket_connect_timeout=settings.client_timeout_seconds,
                socket_timeout=settings.client_timeout_seconds,
            )
        return self._client

    async def ping(self) -> ClientHealth:
        try:
            client = self.connect()
            await client.ping()
            return ClientHealth("redis", True)
        except Exception as exc:
            return ClientHealth("redis", False, str(exc))

    async def get_json(self, key: str) -> Any | None:
        try:
            value = await self.connect().get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        try:
            await self.connect().set(key, json.dumps(value, ensure_ascii=False), ex=ttl or settings.redis_cache_ttl_seconds)
        except Exception:
            return

    async def delete(self, *keys: str) -> None:
        if not keys:
            return
        try:
            await self.connect().delete(*keys)
        except Exception:
            return

    async def delete_pattern(self, pattern: str) -> None:
        try:
            client = self.connect()
            keys = [key async for key in client.scan_iter(match=pattern)]
            if keys:
                await client.delete(*keys)
        except Exception:
            return

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
