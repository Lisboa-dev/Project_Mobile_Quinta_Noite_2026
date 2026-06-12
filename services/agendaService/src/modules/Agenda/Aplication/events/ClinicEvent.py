from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from src.modules.agenda.domain.entities import Clinic
from src.modules.agenda.aplication.events._helpers import rule_ids, utc_now


@dataclass(frozen=True)
class ClinicCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.clinic.created"

    triggered_by_id: str | None
    clinic_id: str
    name: str
    rule_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, clinic: Clinic, triggered_by_id: str | None) -> "ClinicCreatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            clinic_id=str(clinic.id),
            name=clinic.name,
            rule_ids=rule_ids(clinic.rules),
        )


@dataclass(frozen=True)
class ClinicUpdatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.clinic.updated"

    triggered_by_id: str | None
    clinic_id: str
    name: str
    rule_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, clinic: Clinic, triggered_by_id: str | None) -> "ClinicUpdatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            clinic_id=str(clinic.id),
            name=clinic.name,
            rule_ids=rule_ids(clinic.rules),
        )


@dataclass(frozen=True)
class ClinicDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.clinic.deleted"

    triggered_by_id: str | None
    clinic_id: str
    occurred_at: datetime = field(default_factory=utc_now)


CreateClinicEvent = ClinicCreatedEvent
UpdateClinicEvent = ClinicUpdatedEvent
DeleteClinicEvent = ClinicDeletedEvent
