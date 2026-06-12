from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListQuery


class ListRulesUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: ListQuery) -> list[dict[str, Any]]:
        if hasattr(self._repository, "list_rules"):
            return await self._repository.list_rules(query)
        return await self._repository.list(query)
