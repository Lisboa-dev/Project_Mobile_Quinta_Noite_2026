from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListDaysQuery


class ListDaysUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, query: ListDaysQuery) -> list[dict[str, Any]]:
        return await self._repository._list(query)


class ListMonthDaysForFrontUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, year: int, month: int) -> list[dict[str, Any]]:
        return await self._repository.list_month_for_front(year, month)
