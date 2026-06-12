from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar

from src.modules.agenda.domain.entities import Appointment
from src.modules.agenda.aplication.events._helpers import enum_value, text, utc_now


@dataclass(frozen=True)
class AppointmentCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.appointment.created"

    triggered_by_id: str | None
    appointment_id: str
    doctor_id: str
    patient_id: str
    room_id: str
    time: str
    date: str | None = None
    status: str | None = None
    appointment_type: Any = None
    scheduler_id: str | None = None
    occurred_at: datetime = field(
        default_factory=utc_now
    )

    @classmethod
    def from_entity(
        cls,
        appointment: Appointment,
        triggered_by_id: str | None,
        scheduler_id: str | None = None,
    ) -> "AppointmentCreatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            appointment_id=str(appointment.id),
            doctor_id=str(appointment.doctor_id),
            patient_id=str(appointment.patient_id),
            room_id=str(appointment.room_id),
            time=str(appointment.time),
            date=appointment.date,
            status=text(enum_value(appointment.status)),
            appointment_type=enum_value(appointment.appointment_type),
            scheduler_id=scheduler_id,
        )


@dataclass(frozen=True)
class AppointmentUpdatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.appointment.updated"

    triggered_by_id: str | None
    appointment_id: str
    doctor_id: str
    patient_id: str
    room_id: str
    time: str
    date: str | None = None
    status: str | None = None
    appointment_type: Any = None
    occurred_at: datetime = field(
        default_factory=utc_now
    )

    @classmethod
    def from_entity(
        cls,
        appointment: Appointment,
        triggered_by_id: str | None,
    ) -> "AppointmentUpdatedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            appointment_id=str(appointment.id),
            doctor_id=str(appointment.doctor_id),
            patient_id=str(appointment.patient_id),
            room_id=str(appointment.room_id),
            time=str(appointment.time),
            date=appointment.date,
            status=text(enum_value(appointment.status)),
            appointment_type=enum_value(appointment.appointment_type),
        )


@dataclass(frozen=True)
class AppointmentDeletedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.appointment.deleted"

    triggered_by_id: str | None
    appointment_id: str
    doctor_id: str | None = None
    patient_id: str | None = None
    room_id: str | None = None
    time: str | None = None
    date: str | None = None
    status: str | None = None
    occurred_at: datetime = field(
        default_factory=utc_now
    )

    @classmethod
    def from_entity(
        cls,
        appointment: Appointment,
        triggered_by_id: str | None,
    ) -> "AppointmentDeletedEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            appointment_id=str(appointment.id),
            doctor_id=str(appointment.doctor_id),
            patient_id=str(appointment.patient_id),
            room_id=str(appointment.room_id),
            time=str(appointment.time),
            date=appointment.date,
            status=text(enum_value(appointment.status)),
        )


@dataclass(frozen=True)
class CancelAppointmentEvent:
    EVENT_NAME: ClassVar[str] = "agenda.appointment.canceled"

    triggered_by_id: str | None
    appointment_id: str
    doctor_id: str | None = None
    patient_id: str | None = None
    room_id: str | None = None
    time: str | None = None
    date: str | None = None
    status: str | None = None
    occurred_at: datetime = field(
        default_factory=utc_now
    )

    @classmethod
    def from_entity(
        cls,
        appointment: Appointment,
        triggered_by_id: str | None,
    ) -> "CancelAppointmentEvent":
        return cls(
            triggered_by_id=triggered_by_id,
            appointment_id=str(appointment.id),
            doctor_id=str(appointment.doctor_id),
            patient_id=str(appointment.patient_id),
            room_id=str(appointment.room_id),
            time=str(appointment.time),
            date=appointment.date,
            status=text(enum_value(appointment.status)),
        )


CreateAppointmentEvent = AppointmentCreatedEvent
UpdateAppointmentEvent = AppointmentUpdatedEvent


@dataclass(frozen=True)
class AppointmentTypeCreatedEvent:
    EVENT_NAME: ClassVar[str] = "agenda.appointment-type.created"

    triggered_by_id: str | None
    name: str
    duration: int
    description: str | None = None
    occurred_at: datetime = field(default_factory=utc_now)
