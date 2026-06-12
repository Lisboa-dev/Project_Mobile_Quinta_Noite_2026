from typing import Any

import aio_pika

from src.infra.clients.base import ClientHealth
from src.infra.config.settings import settings
from src.infra.mapper.JsonMapper import to_primitive


class RabbitMQClient:
    def __init__(self, url: str | None = None, exchange_name: str | None = None):
        self._url = url or settings.rabbitmq_url
        self._exchange_name = exchange_name or settings.rabbitmq_exchange
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._channel: aio_pika.abc.AbstractChannel | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> aio_pika.abc.AbstractExchange:
        if self._connection is not None and self._connection.is_closed:
            self._channel = None
            self._exchange = None

        if self._exchange is None:
            self._connection = await aio_pika.connect_robust(
                self._url,
                timeout=settings.client_timeout_seconds,
            )
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
        return self._exchange

    async def publish(self, routing_key: str, payload: Any) -> None:
        exchange = await self.connect()
        message = aio_pika.Message(
            body=__import__("json").dumps(to_primitive(payload), ensure_ascii=False).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=routing_key)

    async def consume(self, queue_name: str, routing_keys: list[str], handler) -> None:
        try:
            if self._connection is None or self._connection.is_closed:
                self._connection = await aio_pika.connect_robust(
                    self._url,
                    timeout=settings.client_timeout_seconds,
                )
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            queue = await self._channel.declare_queue(queue_name, durable=True)
            for routing_key in routing_keys:
                await queue.bind(self._exchange, routing_key=routing_key)
            await queue.consume(handler)
        except Exception:
            await self.close()
            raise

    async def ping(self) -> ClientHealth:
        try:
            await self.connect()
            return ClientHealth("rabbitmq", True, metadata={"exchange": self._exchange_name})
        except Exception as exc:
            await self.close()
            return ClientHealth("rabbitmq", False, str(exc))

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None
