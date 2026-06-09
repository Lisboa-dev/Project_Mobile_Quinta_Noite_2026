from dataclasses import dataclass
from datetime import datetime, timezone

import pytest

event_bus_module = pytest.importorskip("src.infra.adapters.EventBus")
events_module = pytest.importorskip("src.modules.users.application.events")


@dataclass(frozen=True)
class UserCreatedEvent:
    user_id: int
    userName: str
    cargo: str
    occurred_at: datetime


def test_users_event_bus_routes_doctor_created_events(monkeypatch):
    published = []

    class FakeBroadcaster:
        async def broadcast(self, payload, routing_key):
            published.append((payload, routing_key))

    bus = event_bus_module.InMemoryEventBus(broadcasters=[FakeBroadcaster()])

    bus.publish(UserCreatedEvent(1, "medico", "MEDICO", datetime.now(timezone.utc)))

    assert published[0][1] == "users.doctor.created"
    assert published[0][0]["event"] == "UserCreatedEvent"


@pytest.mark.parametrize(
    ("event", "routing_key"),
    [
        (
            events_module.MedicCreatedEvent("medic-1", "doc", "Doctor", "doc@example.com"),
            "users.doctor.created",
        ),
        (
            events_module.MedicUpdatedEvent("medic-1", cargo="MEDICO"),
            "users.doctor.updated",
        ),
        (
            events_module.MedicDeletedEvent("medic-1"),
            "users.doctor.deleted",
        ),
        (
            events_module.MedicImageAddedEvent("medic-1", image_url="https://cdn/image.png"),
            "users.doctor.profile-image.updated",
        ),
        (
            events_module.PacientCreatedEvent("patient-1", "patient", "Patient", "patient@example.com"),
            "users.patient.created",
        ),
        (
            events_module.PacientDeletedEvent("patient-1"),
            "users.patient.deleted",
        ),
        (
            events_module.AdminCreatedEvent("admin-1", "admin", "Admin", "admin@example.com"),
            "users.admin.created",
        ),
        (
            events_module.AtendentCreatedEvent("attendant-1", "att", "Attendant", "att@example.com"),
            "users.attendant.created",
        ),
        (
            events_module.UserProfileImageAddedEvent("user-1", profile_image_url="https://cdn/image.png"),
            "users.profile-image.updated",
        ),
    ],
)
def test_users_event_bus_routes_known_events(event, routing_key):
    payload = event_bus_module._payload(event)

    assert event_bus_module._routing_key(payload) == routing_key
