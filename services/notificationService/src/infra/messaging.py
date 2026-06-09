import json
import os
from collections.abc import Awaitable, Callable

import aio_pika

from src.infra.websocket import hub


EventHandler = Callable[[dict, str], Awaitable[None]]


class RabbitMQConsumer:
    def __init__(
        self,
        url: str | None = None,
        queue_name: str | None = None,
        exchanges: list[str] | None = None,
        routing_keys: list[str] | None = None,
    ):
        self.url = url or os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
        self.queue_name = queue_name or os.getenv("NOTIFICATION_EVENTS_QUEUE", "notification.events")
        self.exchanges = exchanges or [
            os.getenv("USER_EVENTS_EXCHANGE", "users.events"),
            os.getenv("RABBITMQ_EXCHANGE", "agenda.events"),
        ]
        configured_keys = os.getenv("NOTIFICATION_EVENT_ROUTING_KEYS", "#")
        self.routing_keys = routing_keys or [key.strip() for key in configured_keys.split(",") if key.strip()]
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    async def start(self, handler: EventHandler) -> None:
        self._connection = await aio_pika.connect_robust(self.url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=20)
        queue = await channel.declare_queue(self.queue_name, durable=True)

        for exchange_name in self.exchanges:
            exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
            for routing_key in self.routing_keys:
                await queue.bind(exchange, routing_key=routing_key)

        async def on_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            async with message.process():
                payload = json.loads(message.body.decode("utf-8"))
                routing_key = message.routing_key or ""
                await handler(payload, routing_key)

        await queue.consume(on_message)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None


async def start_consumer(handler: EventHandler) -> RabbitMQConsumer:
    consumer = RabbitMQConsumer()
    await consumer.start(handler)
    return consumer
