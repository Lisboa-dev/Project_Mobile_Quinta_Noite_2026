from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from src.modules.agenda.domain.entities import Room
from src.modules.agenda.aplication.events._helpers import rule_ids, utc_now


@dataclass(frozen=True)
class RoomCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.room.created"

    triggered_by_id: str | None
    room_id: str
    name: str
    disponibility: bool
    rule_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, room: Room, triggered_by_id: str | None) -> "RoomCreatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            room_id=str(room.id),
            name=room.name,
            disponibility=room.disponibility,
            rule_ids=rule_ids(room.rules),
        )


@dataclass(frozen=True)
class RoomUpdatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.room.updated"

    triggered_by_id: str | None
    room_id: str
    name: str
    disponibility: bool
    rule_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, room: Room, triggered_by_id: str | None) -> "RoomUpdatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            room_id=str(room.id),
            name=room.name,
            disponibility=room.disponibility,
            rule_ids=rule_ids(room.rules),
        )


@dataclass(frozen=True)
class RoomDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.room.deleted"

    triggered_by_id: str | None
    room_id: str
    occurred_at: datetime = field(default_factory=utc_now)


CreateRoomEvent = RoomCreatedEvent
UpdateRoomEvent = RoomUpdatedEvent
DeleteRoomEvent = RoomDeletedEvent
