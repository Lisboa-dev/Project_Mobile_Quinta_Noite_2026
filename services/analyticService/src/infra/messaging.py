import asyncio
import json
import logging
import os

import aio_pika

from src.infra.database import record_event


logger = logging.getLogger(__name__)


async def consume_events() -> None:
    connection = await aio_pika.connect_robust(os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/"))
    channel = await connection.channel()
    queue = await channel.declare_queue(os.getenv("ANALYTIC_EVENTS_QUEUE", "analytic.events"), durable=True)
    for exchange_name in (os.getenv("USER_EVENTS_EXCHANGE", "users.events"), os.getenv("RABBITMQ_EXCHANGE", "agenda.events")):
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
        await queue.bind(exchange, routing_key="#")

    async def handle(message: aio_pika.IncomingMessage):
        async with message.process():
            payload = json.loads(message.body.decode("utf-8"))
            record_event(str(payload.get("event", "event")), message.routing_key, payload)

    await queue.consume(handle)


def start_consumer_task() -> None:
    async def _run():
        try:
            await consume_events()
        except Exception:
            logger.exception("analytic RabbitMQ consumer did not start")

    asyncio.get_running_loop().create_task(_run())
