from collections import defaultdict
import asyncio
import json
import logging
from typing import Any, Callable

from src.infra.adapter.Messaging.websocket.container import connection_manager
from src.infra.clients.rabbitmq import RabbitMQClient
from src.infra.config.settings import settings
from src.infra.database import database
from src.infra.mapper.JsonMapper import to_primitive


logger = logging.getLogger(__name__)


class AwaitableResult:
    def __init__(self, value=None):
        self.value = value

    def __await__(self):
        async def _wrap():
            return self.value

        return _wrap().__await__()


class InMemoryEventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self.events = []
        self._rabbitmq = RabbitMQClient(exchange_name=settings.rabbitmq_exchange)

    def emit(self, event="event", data=None):
        event_name = event.__class__.__name__ if not isinstance(event, str) else event
        payload_data = to_primitive(event if data is None else data)
        payload = {"event": event_name, "data": payload_data}
        self.events.append(payload)
        self._log_event(event_name, event_name, payload)
        self._schedule_publish(event_name, payload)
        self._schedule_websocket(payload)
        for callback in self._subscribers[event_name]:
            callback(data)
        return AwaitableResult(payload)

    def publish(self, event="event", data=None, routing_key: str | None = None):
        event_name = event.__class__.__name__ if not isinstance(event, str) else event
        route = routing_key or event_name
        payload = {"event": event_name, "data": to_primitive(data)}
        self.events.append(payload)
        self._log_event(event_name, route, payload)
        self._schedule_publish(route, payload)
        self._schedule_websocket(payload)
        return AwaitableResult(payload)

    def on(self, event: Any, callback: Callable[..., Any]):
        self._subscribers[event].append(callback)
        return AwaitableResult(True)

    def _log_event(self, event_name: str, routing_key: str, payload: dict) -> None:
        try:
            with database.connect() as connection:
                connection.execute(
                    """
                    INSERT INTO event_logs (service_name, event_name, routing_key, payload)
                    VALUES (?, ?, ?, ?::jsonb)
                    """,
                    ("agenda-service", event_name, routing_key, json.dumps(to_primitive(payload))),
                )
        except Exception:
            logger.exception("failed to persist agenda event log")

    def _schedule_publish(self, routing_key: str, payload: dict) -> None:
        async def _publish():
            try:
                await self._rabbitmq.publish(routing_key, payload)
            except Exception:
                logger.exception("failed to publish agenda event")

        self._schedule(_publish())

    def _schedule_websocket(self, payload: dict) -> None:
        self._schedule(connection_manager.broadcast(payload))

    def _schedule(self, coro) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        loop.create_task(coro)
