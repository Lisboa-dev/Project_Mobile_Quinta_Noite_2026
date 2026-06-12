from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListQuery


class ListAppointmentsByDoctorUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, doctor_id: str, query: ListQuery) -> list[dict[str, Any]]:
        return await self._repository.list_by_doctor(doctor_id, query)
