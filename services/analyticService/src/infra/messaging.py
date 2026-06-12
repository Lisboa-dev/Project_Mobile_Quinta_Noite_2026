import json
from collections.abc import Awaitable, Callable

import aio_pika

from src.infra.settings import settings

EventHandler = Callable[[dict, str], Awaitable[None]]


class RabbitMQConsumer:
    def __init__(self) -> None:
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None

    async def start(self, handler: EventHandler) -> None:
        self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=50)
        queue = await channel.declare_queue(settings.events_queue, durable=True)

        for exchange_name in (settings.user_events_exchange, settings.agenda_events_exchange):
            exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
            for routing_key in settings.routing_keys:
                await queue.bind(exchange, routing_key=routing_key)

        async def on_message(message: aio_pika.abc.AbstractIncomingMessage) -> None:
            async with message.process():
                payload = json.loads(message.body.decode("utf-8"))
                await handler(payload, message.routing_key or "")

        await queue.consume(on_message)

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
