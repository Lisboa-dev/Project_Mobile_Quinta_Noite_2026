from typing import Any

from pydantic import field_validator, model_validator

from src.api.interfaces.base import ApiInput, required_non_empty
from src.modules.agenda.aplication.dtos.useCase.command.RoomUseCasesDTO import UpdateRoomCommand


class CreateRoomRequest(ApiInput):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return required_non_empty(value, "name")


class UpdateRoomRequest(ApiInput):
    name: str | None = None
    disponibility: bool | None = None
    rules: list[Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_non_empty(value, "name")

    @model_validator(mode="after")
    def validate_has_update(self):
        if self.name is None and self.disponibility is None and self.rules is None:
            raise ValueError("at least one field must be provided")
        return self

    def to_command(self, room_id: str) -> UpdateRoomCommand:
        return UpdateRoomCommand(
            id=room_id,
            triggered_by_id=self.triggered_by_id,
            name=self.name,
            disponibility=self.disponibility,
            rules=self.rules,
        )
