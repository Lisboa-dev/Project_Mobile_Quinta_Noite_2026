from pydantic import field_validator

from src.api.interfaces.base import ApiInput, required_non_empty, validate_iso_date_text, validate_time_text
from src.modules.agenda.aplication.dtos.useCase.command.AppointmentUseCasesDTO import (
    CreateAppointmentCommand,
    DeleteAppointmentCommand,
    UpdateAppointmentCommand,
)


class CreateAppointmentRequest(ApiInput):
    scheduler_id: str
    date: str
    weekday: str
    doctor: str
    patient: str
    time: str
    type: str
    room: str | None = None

    @field_validator("scheduler_id", "weekday", "doctor", "patient", "type")
    @classmethod
    def validate_required_text(cls, value: str, info):
        return required_non_empty(value, info.field_name)

    @field_validator("room")
    @classmethod
    def validate_optional_room(cls, value: str | None):
        if value is None:
            return None
        return required_non_empty(value, "room")

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str):
        return validate_iso_date_text(value, "date")

    @field_validator("time")
    @classmethod
    def validate_time(cls, value: str):
        return validate_time_text(value, "time")

    def to_command(self) -> CreateAppointmentCommand:
        return CreateAppointmentCommand(
            scheduler_id=self.scheduler_id,
            date=self.date,
            weekday=self.weekday,
            doctor=self.doctor,
            patient=self.patient,
            time=self.time,
            type=self.type,
            triggered_by_id=self.triggered_by_id,
            room=self.room,
        )


class UpdateAppointmentRequest(ApiInput):
    def to_command(self, appointment_id: str) -> UpdateAppointmentCommand:
        return UpdateAppointmentCommand(id=appointment_id, triggered_by_id=self.triggered_by_id)


class DeleteAppointmentRequest(ApiInput):
    def to_command(self, appointment_id: str) -> DeleteAppointmentCommand:
        return DeleteAppointmentCommand(id=appointment_id, triggered_by_id=self.triggered_by_id)
