from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery
from src.modules.agenda.aplication.useCases.querys.base import GetByIdUseCase


class GetRoomByIdUseCase(GetByIdUseCase):
    pass


class GetRoomAdminDetailUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: GetByIdQuery) -> dict[str, Any] | None:
        return await self._repository.get_admin_detail(query.id)
