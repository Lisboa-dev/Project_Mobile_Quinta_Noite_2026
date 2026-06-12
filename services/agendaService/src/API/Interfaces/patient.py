from pydantic import field_validator, model_validator

from src.api.interfaces.base import ApiInput, required_non_empty
from src.modules.agenda.aplication.dtos.useCase.command.PatientUseCasesDTO import (
    CreatePatientCommand,
    UpdatePatientCommand,
)


class CreatePatientRequest(ApiInput):
    id: str
    name: str

    @field_validator("id", "name")
    @classmethod
    def validate_required_text(cls, value: str, info):
        return required_non_empty(value, info.field_name)

    def to_command(self) -> CreatePatientCommand:
        return CreatePatientCommand(
            id=self.id,
            name=self.name,
            triggered_by_id=self.triggered_by_id,
        )


class UpdatePatientRequest(ApiInput):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_non_empty(value, "name")

    @model_validator(mode="after")
    def validate_has_update(self):
        if self.name is None:
            raise ValueError("at least one field must be provided")
        return self

    def to_command(self, patient_id: str) -> UpdatePatientCommand:
        return UpdatePatientCommand(
            id=patient_id,
            triggered_by_id=self.triggered_by_id,
            name=self.name,
        )
