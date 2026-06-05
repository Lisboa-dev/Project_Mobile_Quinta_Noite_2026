import asyncio
import json
import logging
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, date
from typing import Any

import aio_pika
from sqlalchemy import text

from src.infra.config.db.liteSql.LiteSql import engine


logger = logging.getLogger(__name__)


def _json_default(value: Any):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _payload(event) -> dict:
    if is_dataclass(event):
        data = asdict(event)
    elif isinstance(event, dict):
        data = event
    else:
        data = {"value": str(event)}
    return {"event": event.__class__.__name__, "data": data}


def _routing_key(payload: dict) -> str:
    event = payload["event"]
    data = payload.get("data", {})
    cargo = str(data.get("cargo") or "").upper()
    if event == "UserCreatedEvent" and cargo == "MEDICO":
        return "users.doctor.created"
    if event == "UserDeletedEvent" and cargo == "MEDICO":
        return "users.doctor.deleted"
    if event == "PacientCreatedEvent":
        return "users.patient.created"
    if event == "PacientDeletedEvent":
        return "users.patient.deleted"
    return f"users.{event.removesuffix('Event').lower()}"


class InMemoryEventBus:
    def __init__(self):
        self.events = []
        self._subscribers = []
        self._rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
        self._exchange = os.getenv("USER_EVENTS_EXCHANGE", "users.events")

    def publish(self, event) -> None:
        payload = _payload(event)
        routing_key = _routing_key(payload)
        self.events.append(payload)
        self._log_event(payload, routing_key)
        for callback in self._subscribers:
            callback(payload)
        self._publish_rabbitmq(payload, routing_key)

    def subscribe(self, callback) -> None:
        self._subscribers.append(callback)

    def _log_event(self, payload: dict, routing_key: str) -> None:
        try:
            body = json.dumps(payload, default=_json_default)
            with engine.begin() as connection:
                connection.execute(
                    text(
                        """
                        INSERT INTO event_logs (service_name, event_name, routing_key, payload)
                        VALUES (:service_name, :event_name, :routing_key, CAST(:payload AS JSONB))
                        """
                    ),
                    {
                        "service_name": "users-service",
                        "event_name": payload["event"],
                        "routing_key": routing_key,
                        "payload": body,
                    },
                )
        except Exception:
            logger.exception("failed to persist users event log")

    def _publish_rabbitmq(self, payload: dict, routing_key: str) -> None:
        async def _publish():
            connection = await aio_pika.connect_robust(self._rabbitmq_url)
            async with connection:
                channel = await connection.channel()
                exchange = await channel.declare_exchange(self._exchange, aio_pika.ExchangeType.TOPIC, durable=True)
                await exchange.publish(
                    aio_pika.Message(body=json.dumps(payload, default=_json_default).encode("utf-8")),
                    routing_key=routing_key,
                )

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            try:
                asyncio.run(_publish())
            except Exception:
                logger.exception("failed to publish users event")
        else:
            loop.create_task(_publish())
