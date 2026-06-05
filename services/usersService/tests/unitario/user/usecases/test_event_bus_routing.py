from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import import_module

event_bus_module = import_module("src.infra.adapters.EventBus")


@dataclass(frozen=True)
class UserCreatedEvent:
    user_id: int
    userName: str
    cargo: str
    occurred_at: datetime


def test_users_event_bus_routes_doctor_created_events(monkeypatch):
    logged = []
    published = []
    bus = event_bus_module.InMemoryEventBus()

    monkeypatch.setattr(bus, "_log_event", lambda payload, routing_key: logged.append((payload, routing_key)))
    monkeypatch.setattr(bus, "_publish_rabbitmq", lambda payload, routing_key: published.append((payload, routing_key)))

    bus.publish(UserCreatedEvent(1, "medico", "MEDICO", datetime.now(timezone.utc)))

    assert logged[0][1] == "users.doctor.created"
    assert published[0][0]["event"] == "UserCreatedEvent"
