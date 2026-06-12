from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import GetByIdQuery


class GetRuleByIdUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: GetByIdQuery) -> dict[str, Any] | None:
        if hasattr(self._repository, "detail"):
            return await self._repository.detail(query.id)
        return await self._repository.get_by_id(query.id)
