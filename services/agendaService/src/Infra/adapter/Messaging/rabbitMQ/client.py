from typing import Any, Callable

from src.infra.adapter.Messaging.EventBus import AwaitableResult
from src.infra.clients.rabbitmq import RabbitMQClient


class RabbitMQEventBus:
    def __init__(self, url: str | None = None, exchange_name: str = "agenda.events"):
        self._client = RabbitMQClient(url=url, exchange_name=exchange_name)

    async def connect(self):
        return await self._client.connect()

    def emit(self, event: Any = "event", data: Any = None):
        event_name = self._event_name(event)
        return self.publish(event=event_name, data=event if data is None else data, routing_key=event_name)

    async def publish(self, event: Any = "event", data: Any = None, routing_key: str | None = None):
        await self._client.publish(routing_key or str(event), {"event": event, "data": data})

    def on(self, event: Any, callback: Callable[..., Any]):
        return AwaitableResult(False)

    def _event_name(self, event: Any) -> str:
        if isinstance(event, str):
            return event
        return str(getattr(event, "EVENT_NAME", event.__class__.__name__))

    async def ping(self):
        return await self._client.ping()

    async def close(self) -> None:
        await self._client.close()
