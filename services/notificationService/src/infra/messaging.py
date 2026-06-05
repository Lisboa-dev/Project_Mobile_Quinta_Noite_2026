import asyncio
import json
import logging
import os

import aio_pika

from src.infra.database import log_event
from src.modules.userBell.api.schemas import BellNotificationRequest
from src.modules.userBell.service.context import UserBellContext


logger = logging.getLogger(__name__)


class WebSocketHub:
    def __init__(self):
        self.connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict):
        for websocket in list(self.connections):
            await websocket.send_json(payload)


hub = WebSocketHub()


def _notification_from_event(payload: dict) -> BellNotificationRequest | None:
    event = str(payload.get("event", "event"))
    data = payload.get("data") or {}
    user_id = str(data.get("user_id") or data.get("pacient_id") or data.get("patient_id") or data.get("id") or "system")
    title = event.replace("Event", "")
    return BellNotificationRequest(
        user_id=user_id,
        title=title,
        message=f"Evento recebido: {event}",
        link=None,
        metadata=payload,
    )


async def consume_events() -> None:
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    connection = await aio_pika.connect_robust(url)
    channel = await connection.channel()
    queue = await channel.declare_queue(os.getenv("NOTIFICATION_EVENTS_QUEUE", "notification.events"), durable=True)
    for exchange_name in (os.getenv("USER_EVENTS_EXCHANGE", "users.events"), os.getenv("RABBITMQ_EXCHANGE", "agenda.events")):
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)
        await queue.bind(exchange, routing_key="#")

    async def handle(message: aio_pika.IncomingMessage):
        async with message.process():
            payload = json.loads(message.body.decode("utf-8"))
            log_event(str(payload.get("event", "event")), message.routing_key, payload)
            request = _notification_from_event(payload)
            if request:
                notification = UserBellContext.create_notification_service().execute(request)
                await hub.broadcast({"event": "notification.created", "data": notification})

    await queue.consume(handle)


def start_consumer_task() -> None:
    async def _run():
        try:
            await consume_events()
        except Exception:
            logger.exception("notification RabbitMQ consumer did not start")

    asyncio.get_running_loop().create_task(_run())
