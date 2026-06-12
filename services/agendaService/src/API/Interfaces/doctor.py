from typing import Any

from pydantic import field_validator, model_validator

from src.api.interfaces.base import ApiInput, required_non_empty
from src.modules.agenda.aplication.dtos.useCase.command.DoctorUseCasesDTO import (
    CreateDoctorCommand,
    UpdateDoctorCommand,
)


class CreateDoctorRequest(ApiInput):
    id_extern: str
    name: str

    @field_validator("id_extern", "name")
    @classmethod
    def validate_required_text(cls, value: str, info):
        return required_non_empty(value, info.field_name)

    def to_command(self) -> CreateDoctorCommand:
        return CreateDoctorCommand(
            id_extern=self.id_extern,
            name=self.name,
            triggered_by_id=self.triggered_by_id,
        )


class UpdateDoctorRequest(ApiInput):
    name: str | None = None
    availability: bool | None = None
    rules: list[Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_non_empty(value, "name")

    @model_validator(mode="after")
    def validate_has_update(self):
        if self.name is None and self.availability is None and self.rules is None:
            raise ValueError("at least one field must be provided")
        return self

    def to_command(self, doctor_id: str) -> UpdateDoctorCommand:
        return UpdateDoctorCommand(
            id=doctor_id,
            triggered_by_id=self.triggered_by_id,
            name=self.name,
            availability=self.availability,
            rules=self.rules,
        )
