import asyncio
import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Any, Protocol

from src.infra.clients import PrometheusClient, RabbitMQClient, RedisClient
from src.infra.config.settings import settings
from src.infra.config.db.liteSql.LiteSql import get_query
from src.infra.models.sqlAlchemy.UserSqlSchamy import EventLog


logger = logging.getLogger(__name__)


class EventBroadcaster(Protocol):
    async def broadcast(self, payload: dict, routing_key: str) -> None: ...


def _json_default(value: Any):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _to_primitive(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _to_primitive(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): _to_primitive(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_primitive(item) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _payload(event) -> dict:
    if is_dataclass(event) and not isinstance(event, type):
        data = _to_primitive(event)
    elif isinstance(event, dict):
        data = _to_primitive(event)
    else:
        data = {"value": str(event)}
    event_name = event.__name__ if isinstance(event, type) else event.__class__.__name__
    return {"event": event_name, "data": data}


def _routing_key(payload: dict) -> str:
    event = payload["event"]
    data = payload.get("data", {})
    cargo = str(data.get("cargo") or "").upper()

    if event in {"UserCreatedEvent", "MedicCreatedEvent"} and cargo == "MEDICO":
        return "users.doctor.created"
    if event in {"UserDeletedEvent", "MedicDeletedEvent"} and cargo == "MEDICO":
        return "users.doctor.deleted"
    if event in {"UserUpdatedEvent", "MedicUpdatedEvent"} and cargo == "MEDICO":
        return "users.doctor.updated"
    if event == "MedicImageAddedEvent":
        return "users.doctor.profile-image.updated"
    if event == "PacientCreatedEvent":
        return "users.patient.created"
    if event == "PacientDeletedEvent":
        return "users.patient.deleted"
    if event == "AdminCreatedEvent":
        return "users.admin.created"
    if event == "AdminUpdatedEvent":
        return "users.admin.updated"
    if event == "AdminDeletedEvent":
        return "users.admin.deleted"
    if event == "AtendentCreatedEvent":
        return "users.attendant.created"
    if event == "AtendentUpdatedEvent":
        return "users.attendant.updated"
    if event == "AtendentDeletedEvent":
        return "users.attendant.deleted"
    if event == "UserPromotedEvent":
        return "users.user.promoted"
    if event == "UserDepreciatEvent":
        return "users.user.depreciated"
    if event == "UserProfileImageAddedEvent":
        return "users.profile-image.updated"
    return f"users.{event.removesuffix('Event').lower()}"


class InMemoryBroadcaster:
    def __init__(self):
        self.events: list[dict] = []
        self.subscribers = []

    async def broadcast(self, payload: dict, routing_key: str) -> None:
        self.events.append(payload)
        for callback in list(self.subscribers):
            callback(payload)

    def subscribe(self, callback) -> None:
        self.subscribers.append(callback)


class PostgresEventLogBroadcaster:
    async def broadcast(self, payload: dict, routing_key: str) -> None:
        with get_query() as session:
            session.add(
                EventLog(
                    service_name=settings.service_name,
                    event_name=payload["event"],
                    routing_key=routing_key,
                    payload=json.loads(json.dumps(payload, default=_json_default)),
                )
            )


class RabbitMQEventBroadcaster:
    def __init__(self, client: RabbitMQClient | None = None):
        self._client = client or RabbitMQClient()

    async def broadcast(self, payload: dict, routing_key: str) -> None:
        await self._client.publish(routing_key, payload)


class RedisEventBroadcaster:
    def __init__(self, client: RedisClient | None = None, channel: str | None = None):
        self._client = client or RedisClient()
        self._channel = channel or settings.redis_events_channel

    async def broadcast(self, payload: dict, routing_key: str) -> None:
        await self._client.publish_json(self._channel, {"routing_key": routing_key, **payload})


class PrometheusEventBroadcaster:
    def __init__(self, client: PrometheusClient | None = None):
        self._client = client or PrometheusClient()
        self.events_total: dict[str, int] = {}

    async def broadcast(self, payload: dict, routing_key: str) -> None:
        self.events_total[routing_key] = self.events_total.get(routing_key, 0) + 1

    def health(self):
        return self._client.ping()


class BroadcastEventBus:
    def __init__(self, broadcasters: list[EventBroadcaster] | None = None):
        self.memory = InMemoryBroadcaster()
        self._broadcasters = broadcasters or [
            self.memory,
            PostgresEventLogBroadcaster(),
            RabbitMQEventBroadcaster(),
            RedisEventBroadcaster(),
            PrometheusEventBroadcaster(),
        ]

    @property
    def events(self) -> list[dict]:
        return self.memory.events

    def subscribe(self, callback) -> None:
        self.memory.subscribe(callback)

    def _log_event(self, payload: dict, routing_key: str) -> None:
        asyncio.run(PostgresEventLogBroadcaster().broadcast(payload, routing_key))

    def _publish_rabbitmq(self, payload: dict, routing_key: str) -> None:
        asyncio.run(RabbitMQEventBroadcaster().broadcast(payload, routing_key))

    def publish(self, event) -> None:
        payload = _payload(event)
        routing_key = _routing_key(payload)

        async def _broadcast_all():
            for broadcaster in self._broadcasters:
                try:
                    await broadcaster.broadcast(payload, routing_key)
                except Exception:
                    logger.exception("failed to broadcast users event through %s", broadcaster.__class__.__name__)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(_broadcast_all())
        else:
            loop.create_task(_broadcast_all())


InMemoryEventBus = BroadcastEventBus
