from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListQuery


class ListAppointmentsByPatientUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, patient_id: str, query: ListQuery) -> list[dict[str, Any]]:
        return await self._repository.list_by_patient(patient_id, query)
