import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.infra.adapter.ExternServices.CalendarDataClient import CalendarDataClient
from src.infra.adapter.Messaging.websocket.connectManager import ConnectionManager
from src.api.router import api_router
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.useCases.commands.calendar.CreateCalendar import (
    CreateCalendarCommand,
    CreateCalendarUseCase,
)
from tests.provider import AgendaTestProvider


def test_create_calendar_persists_and_returns_output():
    async def run():
        provider = AgendaTestProvider()
        repository = provider.calendar_repository()
        bus = provider.event_bus()
        use_case = provider.create_calendar_use_case(repository=repository, bus=bus)

        result = await use_case.execute(CreateCalendarCommand(day=1, ano=2026))

        assert result.success is True
        assert result.resource == "calendar"
        assert result.data["days_count"] == 2
        assert len(repository.days) == 2
        assert len(bus.events) == 1
        assert bus.events[0].year == "2026"

    asyncio.run(run())


def test_calendar_data_client_generates_requested_month_and_leap_year():
    async def run():
        client = CalendarDataClient()

        february_2024 = await client.mont(2, 2024)
        february_2023 = await client.mont(2, 2023)

        assert len(february_2024) == 29
        assert len(february_2023) == 28
        assert {day["date"].month for day in february_2024} == {2}
        assert february_2024[0]["date"].day == 1
        assert february_2024[-1]["date"].day == 29

    asyncio.run(run())


def test_create_calendar_rolls_back_year_when_day_creation_fails():
    class FailingCalendarRepository:
        def __init__(self):
            self.saved = []
            self.deleted_years = []

        async def save(self, day):
            self.saved.append(day)
            if len(self.saved) == 2:
                raise RuntimeError("save failed")

        async def delete(self, ano=None):
            self.deleted_years.append(ano)

    class EmptyRuleRepository:
        async def getDayRules(self):
            return []

    class TwoDayCalendarData:
        async def mont(self, month, year):
            days = await CalendarDataClient().mont(month, year)
            return days[:2]

    async def run():
        repository = FailingCalendarRepository()
        use_case = CreateCalendarUseCase(
            repository,
            EmptyRuleRepository(),
            TwoDayCalendarData(),
            AgendaTestProvider().event_bus(),
        )

        with pytest.raises(CreateUseCaseException):
            await use_case.execute(CreateCalendarCommand(day=1, ano=2026))

        assert repository.deleted_years == [2026]

    asyncio.run(run())


def test_websocket_manager_broadcasts_and_discards_closed_connections():
    class FakeWebSocket:
        def __init__(self, fail=False):
            self.fail = fail
            self.messages = []

        async def send_json(self, message):
            if self.fail:
                raise RuntimeError("closed")
            self.messages.append(message)

    async def run():
        manager = ConnectionManager()
        active = FakeWebSocket()
        closed = FakeWebSocket(fail=True)
        manager.active_connections = [active, closed]

        await manager.broadcast({"event": "agenda.calendar.created"})

        assert active.messages == [{"event": "agenda.calendar.created"}]
        assert manager.active_connections == [active]

    asyncio.run(run())


def test_agenda_websocket_endpoint_accepts_connection():
    app = FastAPI()
    app.include_router(api_router)

    with TestClient(app).websocket_connect("/agenda/ws") as websocket:
        websocket.send_text("ping")


def test_agenda_openapi_does_not_expose_doctor_or_patient_routes():
    app = FastAPI()
    app.include_router(api_router)

    paths = app.openapi()["paths"]

    assert not any(path.startswith("/agenda/doctors") for path in paths)
    assert not any(path.startswith("/agenda/patients") for path in paths)
    assert all(path.startswith(("/agenda/appointments", "/agenda/rooms")) for path in paths)


def test_room_routes_require_admin_role():
    app = FastAPI()
    app.include_router(api_router)

    response = TestClient(app).get("/agenda/rooms/")

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin role required"
