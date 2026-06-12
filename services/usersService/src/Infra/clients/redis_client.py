import json
from typing import Any

from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings


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

    async def publish_json(self, channel: str, payload: Any) -> None:
        await self.connect().publish(channel, json.dumps(payload, ensure_ascii=False, default=str))

    async def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        await self.connect().set(
            key,
            json.dumps(value, ensure_ascii=False, default=str),
            ex=ttl or settings.redis_cache_ttl_seconds,
        )

    async def ping(self) -> ClientHealth:
        try:
            await self.connect().ping()
            return ClientHealth("redis", True)
        except Exception as exc:
            return ClientHealth("redis", False, str(exc))

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
