import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any, Callable

from src.infra.adapter.Messaging.websocket.container import connection_manager
from src.infra.cache import RuleOptimizationCache
from src.infra.clients.rabbitmq import RabbitMQClient
from src.infra.config.settings import settings
from src.infra.mapper.JsonMapper import to_primitive


logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PendingBrokerEvent:
    routing_key: str
    payload: dict[str, Any]
    attempts: int = 0
    created_at: str = field(default_factory=_utc_now)
    last_error: str | None = None


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
        self._rule_optimization_cache = RuleOptimizationCache()
        self._pending_events: deque[PendingBrokerEvent] = deque()
        self._max_pending_events = max(1, settings.event_broker_buffer_max_size)
        self._retry_interval_seconds = max(1.0, settings.event_broker_retry_interval_seconds)
        self._retry_batch_size = max(1, settings.event_broker_retry_batch_size)
        self._dropped_events = 0
        self._broker_online: bool | None = None
        self._last_error: str | None = None
        self._last_success_at: str | None = None
        self._last_flush_at: str | None = None
        self._flush_running = False
        self._flush_task: asyncio.Task | None = None

    def emit(self, event="event", data=None):
        event_name = self._event_name(event)
        payload_data = to_primitive(event if data is None else data)
        payload = {"event": event_name, "data": payload_data}
        self.events.append(payload)
        self._schedule_publish(event_name, payload)
        self._schedule_websocket(payload)
        self._schedule_rule_optimization(event_name)
        for callback in self._subscribers[event_name]:
            callback(data)
        return AwaitableResult(payload)

    def publish(self, event="event", data=None, routing_key: str | None = None):
        event_name = self._event_name(event)
        route = routing_key or event_name
        payload = {"event": event_name, "data": to_primitive(data)}
        self.events.append(payload)
        self._schedule_publish(route, payload)
        self._schedule_websocket(payload)
        self._schedule_rule_optimization(event_name)
        return AwaitableResult(payload)

    def on(self, event: Any, callback: Callable[..., Any]):
        self._subscribers[event].append(callback)
        return AwaitableResult(True)

    def _event_name(self, event: Any) -> str:
        if isinstance(event, str):
            return event
        return str(getattr(event, "EVENT_NAME", event.__class__.__name__))

    def start(self) -> None:
        self._ensure_flush_worker()

    async def stop(self) -> None:
        if self._flush_task is not None:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None
        await self.flush_pending()
        await self._rabbitmq.close()

    def buffer_status(self) -> dict[str, Any]:
        oldest = self._pending_events[0] if self._pending_events else None
        return {
            "broker_online": self._broker_online,
            "pending_events": len(self._pending_events),
            "max_pending_events": self._max_pending_events,
            "dropped_events": self._dropped_events,
            "retry_interval_seconds": self._retry_interval_seconds,
            "retry_batch_size": self._retry_batch_size,
            "flush_running": self._flush_running,
            "last_error": self._last_error,
            "last_success_at": self._last_success_at,
            "last_flush_at": self._last_flush_at,
            "oldest_pending_event": (
                {
                    "routing_key": oldest.routing_key,
                    "attempts": oldest.attempts,
                    "created_at": oldest.created_at,
                    "last_error": oldest.last_error,
                }
                if oldest is not None
                else None
            ),
        }

    async def broker_health(self):
        health = await self._rabbitmq.ping()
        self._broker_online = health.ok
        if health.ok:
            self._last_error = None
            self._ensure_flush_worker()
        else:
            self._last_error = health.detail
        return health

    async def flush_pending(self) -> dict[str, Any]:
        if self._flush_running or not self._pending_events:
            return self.buffer_status()

        self._flush_running = True
        flushed = 0
        try:
            for _ in range(min(self._retry_batch_size, len(self._pending_events))):
                pending_event = self._pending_events[0]
                published = await self._publish_now(pending_event.routing_key, pending_event.payload)
                if not published:
                    pending_event.attempts += 1
                    pending_event.last_error = self._last_error
                    break
                self._pending_events.popleft()
                flushed += 1
            self._last_flush_at = _utc_now()
        finally:
            self._flush_running = False

        status = self.buffer_status()
        status["flushed_events"] = flushed
        return status

    def _schedule_publish(self, routing_key: str, payload: dict) -> None:
        async def _publish():
            published = await self._publish_now(routing_key, payload)
            if not published:
                self._enqueue_pending(routing_key, payload, self._last_error)

        self._schedule(_publish())

    def _schedule_websocket(self, payload: dict) -> None:
        self._schedule(connection_manager.broadcast(payload))

    def _schedule_rule_optimization(self, event_name: str) -> None:
        if not event_name.startswith("agenda.rule."):
            return
        self._schedule(self._refresh_rule_optimization_cache())

    async def _refresh_rule_optimization_cache(self) -> None:
        try:
            await self._rule_optimization_cache.refresh_all_layers()
        except Exception:
            logger.exception("failed to refresh optimized rule cache")

    async def _publish_now(self, routing_key: str, payload: dict) -> bool:
        try:
            await self._rabbitmq.publish(routing_key, payload)
        except Exception as exc:
            self._broker_online = False
            self._last_error = str(exc)
            await self._rabbitmq.close()
            logger.warning("agenda event broker unavailable; event retained in memory")
            return False

        self._broker_online = True
        self._last_error = None
        self._last_success_at = _utc_now()
        return True

    def _enqueue_pending(self, routing_key: str, payload: dict, error: str | None) -> None:
        if len(self._pending_events) >= self._max_pending_events:
            self._pending_events.popleft()
            self._dropped_events += 1
            logger.error("agenda in-memory event buffer is full; oldest pending event was discarded")

        self._pending_events.append(
            PendingBrokerEvent(
                routing_key=routing_key,
                payload=payload,
                attempts=1,
                last_error=error,
            )
        )
        self._ensure_flush_worker()

    def _ensure_flush_worker(self) -> None:
        if self._flush_task is not None and not self._flush_task.done():
            return
        self._flush_task = self._schedule(self._flush_loop())

    async def _flush_loop(self) -> None:
        while True:
            await asyncio.sleep(self._retry_interval_seconds)
            await self.flush_pending()

    def _schedule(self, coro) -> asyncio.Task | None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            coro.close()
            return
        return loop.create_task(coro)
