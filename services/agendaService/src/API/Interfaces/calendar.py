from typing import Any

from pydantic import field_validator

from src.api.interfaces.base import ApiInput
from src.modules.agenda.aplication.useCases.commands.calendar.CreateCalendar import CreateCalendarCommand
from src.modules.agenda.aplication.useCases.commands.calendar.UpdateDay import UpdateDayCommand


class CreateCalendarRequest(ApiInput):
    mes: int
    ano: int

    @field_validator("mes")
    @classmethod
    def validate_month(cls, value: int) -> int:
        if value < 1 or value > 12:
            raise ValueError("mes must be between 1 and 12")
        return value

    @field_validator("ano")
    @classmethod
    def validate_year(cls, value: int) -> int:
        if value < 1900 or value > 2200:
            raise ValueError("ano must be between 1900 and 2200")
        return value

    def to_command(self) -> CreateCalendarCommand:
        return CreateCalendarCommand(day=self.mes, ano=self.ano, triggered_by_id=self.triggered_by_id)


class UpdateDayRequest(ApiInput):
    data: dict[str, Any]

    @field_validator("data")
    @classmethod
    def validate_data(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("data cannot be empty")
        return value

    def to_command(self, day_id: str) -> UpdateDayCommand:
        return UpdateDayCommand(id=day_id, data=self.data, triggered_by_id=self.triggered_by_id)
