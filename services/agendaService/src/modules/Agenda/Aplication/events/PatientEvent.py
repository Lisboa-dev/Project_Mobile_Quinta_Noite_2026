from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from src.modules.agenda.domain.entities import Patient
from src.modules.agenda.aplication.events._helpers import id_list, text, utc_now


@dataclass(frozen=True)
class PatientCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.patient.created"

    triggered_by_id: str | None
    patient_id: str
    extern_id: str | None
    name: str
    appointment_ids: list[str]
    occurred_at: datetime = field(default_factory=utc_now)

    @classmethod
    def from_entity(cls, patient: Patient, triggered_by_id: str | None) -> "PatientCreatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            patient_id=str(patient.id),
            extern_id=text(patient.extern_id),
            name=patient.name,
            appointment_ids=id_list(patient.appointments),
        )


@dataclass(frozen=True)
class PatientDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.patient.deleted"

    triggered_by_id: str | None
    patient_id: str
    occurred_at: datetime = field(default_factory=utc_now)


CreatePatientEvent = PatientCreatedEvent
DeletePatientEvent = PatientDeletedEvent
