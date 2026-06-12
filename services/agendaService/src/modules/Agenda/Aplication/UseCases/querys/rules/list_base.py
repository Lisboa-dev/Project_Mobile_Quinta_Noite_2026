from typing import Any


class GetRulesAdminContextUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self) -> dict[str, Any]:
        return await self._repository.admin_context()
