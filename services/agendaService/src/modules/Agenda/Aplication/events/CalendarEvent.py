from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from src.modules.agenda.domain.entities import Day
from src.modules.agenda.aplication.events._helpers import enum_value, id_list, utc_now


@dataclass(frozen=True)
class CalendarCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.calendar.created"

    triggered_by_id: str | None
    year: str
    day_ids: list[str]
    days_count: int
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_days(cls, days: list[Day], year: str, triggered_by_id: str | None) -> "CalendarCreatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            year=year,
            day_ids=[str(day.date) for day in days],
            days_count=len(days),
        )


@dataclass(frozen=True)
class DayUpdatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.day.updated"

    triggered_by_id: str | None
    day_id: str
    date: str
    weekday: int
    availability: bool
    status: str
    room_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, day: Day, triggered_by_id: str | None) -> "DayUpdatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            day_id=str(day.date),
            date=str(day.date),
            weekday=day.weekday,
            availability=day.availability,
            status=str(enum_value(day.status)),
            room_ids=id_list(day.rooms),
        )


@dataclass(frozen=True)
class CalendarDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.calendar.deleted"

    triggered_by_id: str | None
    year: str
    occurred_at: datetime = field(default_factory=utc_now)


CreateCalendarEvent = CalendarCreatedEvent
UpdateDayEvent = DayUpdatedEvent
DeleteCalendarEvent = CalendarDeletedEvent
