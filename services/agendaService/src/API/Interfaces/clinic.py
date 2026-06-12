from typing import Any

from pydantic import Field, field_validator

from src.api.interfaces.base import ApiInput, required_non_empty
from src.modules.agenda.aplication.dtos.useCase.command.ClinicUseCasesDTO import (
    CreateClinicCommand,
    UpdateClinicCommand,
)


class CreateClinicRequest(ApiInput):
    name: str
    rules: list[Any] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return required_non_empty(value, "name")

    def to_command(self) -> CreateClinicCommand:
        return CreateClinicCommand(
            name=self.name,
            triggered_by_id=self.triggered_by_id,
            rules=self.rules,
        )


class UpdateClinicRequest(ApiInput):
    name: str | None = None
    rules: list[Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_non_empty(value, "name")

    def to_command(self, clinic_id: str) -> UpdateClinicCommand:
        return UpdateClinicCommand(
            id=clinic_id,
            triggered_by_id=self.triggered_by_id,
            name=self.name,
            rules=self.rules,
        )
