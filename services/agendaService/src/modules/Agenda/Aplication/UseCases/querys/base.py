from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery, ListQuery


class GetByIdUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: GetByIdQuery) -> dict[str, Any] | None:
        return await self._repository.get_by_id(query.id)


class ListUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: ListQuery) -> list[dict[str, Any]]:
        return await self._repository._list(query)
