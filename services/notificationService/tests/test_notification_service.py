import pytest

from src.services import NotificationDispatcher, NotificationQueryService


class FakeWebSocketHub:
    def __init__(self) -> None:
        self.payloads: list[dict] = []

    async def broadcast(self, payload: dict) -> None:
        self.payloads.append(payload)


@pytest.mark.asyncio
async def test_dispatch_event_creates_notification_and_broadcasts(monkeypatch, fake_repository, fake_hub):
    logged_events = []
    monkeypatch.setattr(
        "src.services.notification_service.log_event",
        lambda event_name, routing_key, payload: logged_events.append((event_name, routing_key, payload)),
    )
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event(
        {
            "event": "custom.updated",
            "data": {
                "user_id": "user-2",
                "title": "Consulta atualizada",
                "message": "Seu horario mudou.",
                "link": "/agenda/apt-2",
            },
        },
        "custom.updated",
    )

    assert logged_events[0][0] == "custom.updated"
    assert fake_repository.created[0]["user_id"] == "user-2"
    assert fake_repository.created[0]["metadata"]["routing_key"] == "custom.updated"
    assert fake_hub.payloads[0]["event"] == "notification.created"
    assert fake_hub.payloads[0]["data"]["title"] == "Consulta atualizada"


@pytest.mark.asyncio
async def test_dispatch_event_ignores_payload_without_user(monkeypatch, fake_repository, fake_hub):
    logged_events = []
    monkeypatch.setattr(
        "src.services.notification_service.log_event",
        lambda event_name, routing_key, payload: logged_events.append(event_name),
    )
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event({"event": "system.started", "data": {"message": "ok"}}, "system.started")

    assert logged_events == ["system.started"]
    assert fake_repository.created == []
    assert fake_hub.payloads == []


@pytest.mark.asyncio
async def test_dispatch_event_broadcasts_raw_event_to_events_hub(monkeypatch, fake_repository):
    monkeypatch.setattr("src.services.notification_service.log_event", lambda *args: None)
    notifications_hub = FakeWebSocketHub()
    events_hub = FakeWebSocketHub()
    dispatcher = NotificationDispatcher(
        repository=fake_repository,
        notifications_hub=notifications_hub,
        events_hub=events_hub,
    )

    await dispatcher.dispatch_event({"event": "system.started", "data": {"message": "ok"}}, "system.started")

    assert fake_repository.created == []
    assert notifications_hub.payloads == []
    assert events_hub.payloads == [
        {
            "event": "event.received",
            "routing_key": "system.started",
            "data": {"event": "system.started", "data": {"message": "ok"}},
        }
    ]


def test_dispatcher_builds_defaults_from_event_name(fake_repository, fake_hub):
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    notifications = dispatcher._build_notifications(
        {"type": "custom.created", "data": {"doctorId": "doctor-1"}},
        "custom.created",
        "custom.created",
    )
    notification = notifications[0]

    assert notification["user_id"] == "doctor-1"
    assert notification["title"] == "Custom Created"
    assert notification["message"] == "Evento recebido: custom.created"
    assert notification["channel"] == "bell"


@pytest.mark.asyncio
async def test_dispatch_event_notifies_each_distinct_recipient(monkeypatch, fake_repository, fake_hub):
    monkeypatch.setattr("src.services.notification_service.log_event", lambda *args: None)
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event(
        {
            "event": "agenda.appointment.created",
            "data": {
                "patient_id": "patient-1",
                "doctor_id": "doctor-1",
                "scheduler_id": "patient-1",
                "appointment_id": "apt-1",
                "appointment_type": "retorno",
            },
        },
        "agenda.appointment.created",
    )

    recipients = [notification["user_id"] for notification in fake_repository.created]
    assert recipients == ["doctor-1", "patient-1"]
    assert len(fake_hub.payloads) == 2


@pytest.mark.asyncio
async def test_new_regular_appointment_notifies_doctor_only(monkeypatch, fake_repository, fake_hub):
    monkeypatch.setattr("src.services.notification_service.log_event", lambda *args: None)
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event(
        {
            "event": "agenda.appointment.created",
            "data": {
                "patient_id": "patient-1",
                "doctor_id": "doctor-1",
                "appointment_id": "apt-1",
                "appointment_type": "consulta",
            },
        },
        "agenda.appointment.created",
    )

    assert [notification["user_id"] for notification in fake_repository.created] == ["doctor-1"]
    assert fake_repository.created[0]["title"] == "Nova consulta agendada"


@pytest.mark.asyncio
async def test_return_appointment_notifies_patient_and_doctor(monkeypatch, fake_repository, fake_hub):
    monkeypatch.setattr("src.services.notification_service.log_event", lambda *args: None)
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event(
        {
            "event": "agenda.appointment.created",
            "data": {
                "patient_id": "patient-1",
                "doctor_id": "doctor-1",
                "appointment_id": "apt-2",
                "appointment_type": "re-consulta",
                "date": "2026-06-10",
                "time": "10:00",
            },
        },
        "agenda.appointment.created",
    )

    assert [notification["user_id"] for notification in fake_repository.created] == ["doctor-1", "patient-1"]
    assert fake_repository.created[1]["title"] == "Re-consulta agendada"


@pytest.mark.asyncio
async def test_status_change_notifies_patient(monkeypatch, fake_repository, fake_hub):
    monkeypatch.setattr("src.services.notification_service.log_event", lambda *args: None)
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event(
        {
            "event": "agenda.appointment.updated",
            "data": {
                "patient_id": "patient-1",
                "doctor_id": "doctor-1",
                "appointment_id": "apt-3",
                "status": "CONFIRMED",
            },
        },
        "agenda.appointment.updated",
    )

    assert [notification["user_id"] for notification in fake_repository.created] == ["patient-1"]
    assert fake_repository.created[0]["title"] == "Status da consulta alterado"


@pytest.mark.asyncio
async def test_doctor_created_notifies_admin_channel(monkeypatch, fake_repository, fake_hub):
    monkeypatch.setattr("src.services.notification_service.log_event", lambda *args: None)
    dispatcher = NotificationDispatcher(repository=fake_repository, hub=fake_hub)

    await dispatcher.dispatch_event(
        {"event": "MedicCreatedEvent", "data": {"id": "doctor-1", "name": "Dra Ana"}},
        "users.doctor.created",
    )

    assert [notification["user_id"] for notification in fake_repository.created] == ["admin"]
    assert fake_repository.created[0]["title"] == "Novo medico criado"


def test_query_service_lists_counts_and_marks_read(fake_repository):
    service = NotificationQueryService(fake_repository)

    assert len(service.list_by_user("user-1")) == 1
    assert service.count_unread("user-1") == 1

    updated = service.mark_read("notification-1")

    assert updated["read"] is True
    assert service.count_unread("user-1") == 0
