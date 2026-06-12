import os

from src.modules.agenda.aplication.useCases.commands.calendar.CreateCalendar import CreateCalendarUseCase

from tests import mock_data


def use_mock_data() -> bool:
    return os.getenv("TEST_USE_MOCK_DATA", "true").lower() in {"1", "true", "yes", "on"}


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
        return mock_data.base_day_rules() if use_mock_data() else []


class FakeCalendarData:
    async def mont(self, _month, _year):
        return mock_data.calendar_days()


class FakeBus:
    def __init__(self):
        self.events = []

    async def emit(self, event):
        self.events.append(event)
        return {"event": getattr(event, "EVENT_NAME", event.__class__.__name__)}


class AgendaTestProvider:
    def calendar_repository(self) -> FakeCalendarRepository:
        return FakeCalendarRepository()

    def rule_repository(self) -> FakeRuleRepository:
        return FakeRuleRepository()

    def calendar_data(self) -> FakeCalendarData:
        return FakeCalendarData()

    def event_bus(self) -> FakeBus:
        return FakeBus()

    def create_calendar_use_case(self, repository=None, bus=None) -> CreateCalendarUseCase:
        return CreateCalendarUseCase(
            repository or self.calendar_repository(),
            self.rule_repository(),
            self.calendar_data(),
            bus or self.event_bus(),
        )
