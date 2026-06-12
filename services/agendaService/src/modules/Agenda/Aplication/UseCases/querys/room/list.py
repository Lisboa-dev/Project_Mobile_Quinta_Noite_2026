from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListQuery
from src.modules.agenda.aplication.useCases.querys.base import ListUseCase


class ListRoomsUseCase(ListUseCase):
    pass


class ListRoomsAdminDetailedUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: ListQuery) -> list[dict[str, Any]]:
        return await self._repository.list_admin_detailed(query)
