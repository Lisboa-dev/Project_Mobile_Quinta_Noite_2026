from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from src.modules.agenda.domain.entities import Doctor
from src.modules.agenda.aplication.events._helpers import rule_ids, text, utc_now


@dataclass(frozen=True)
class DoctorCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.doctor.created"

    triggered_by_id: str | None
    doctor_id: str
    extern_id: str | None
    name: str
    availability: bool
    rule_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, doctor: Doctor, triggered_by_id: str | None) -> "DoctorCreatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            doctor_id=str(doctor.id),
            extern_id=text(doctor.extern_id),
            name=doctor.name,
            availability=doctor.availability,
            rule_ids=rule_ids(doctor.rules),
        )


@dataclass(frozen=True)
class DoctorUpdatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.doctor.updated"

    triggered_by_id: str | None
    doctor_id: str
    extern_id: str | None
    name: str
    availability: bool
    rule_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, doctor: Doctor, triggered_by_id: str | None) -> "DoctorUpdatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            doctor_id=str(doctor.id),
            extern_id=text(doctor.extern_id),
            name=doctor.name,
            availability=doctor.availability,
            rule_ids=rule_ids(doctor.rules),
        )


@dataclass(frozen=True)
class DoctorDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.doctor.deleted"

    triggered_by_id: str | None
    doctor_id: str
    occurred_at: datetime = field(default_factory=utc_now)


CreateDoctorEvent = DoctorCreatedEvent
UpdateDoctorEvent = DoctorUpdatedEvent
DeleteDoctorEvent = DoctorDeletedEvent
