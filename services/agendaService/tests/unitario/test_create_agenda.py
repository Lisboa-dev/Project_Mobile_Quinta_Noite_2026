import pytest

from src.modules.agenda.aplication.useCases.commands.calendar.CreateCalendar import (
    CreateCalendarCommand,
    CreateCalendarUseCase,
)


class FakeCalendarRepository:
    def __init__(self):
        self.days = []
        self.deleted_years = []

    async def save(self, day):
        self.days.append(day)

    async def delete(self, ano=None):
        self.deleted_years.append(ano)
        self.days.clear()


class FakeRuleRepository:
    async def getDayRules(self):
        return []


class FakeCalendarData:
    async def mont(self, _month, year):
        from src.infra.adapter.ExternServices.CalendarDataClient import CalendarDataClient

        return await CalendarDataClient().mont(1, year)


class FakeBus:
    def __init__(self):
        self.events = []

    def emit(self, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_create_calendar_persists_and_returns_365_days():
    repository = FakeCalendarRepository()
    bus = FakeBus()
    use_case = CreateCalendarUseCase(repository, FakeRuleRepository(), FakeCalendarData(), bus)

    result = await use_case.execute(CreateCalendarCommand(day=1, ano=2026))

    assert len(result) == 365
    assert len(repository.days) == 365
    assert len(bus.events) == 1
    assert bus.events[0].year == "2026"
