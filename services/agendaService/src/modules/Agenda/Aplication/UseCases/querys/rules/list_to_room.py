from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListQuery


class ListRulesToRoomUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, room_id: str, query: ListQuery) -> list[dict[str, Any]]:
        context = await self._repository.admin_context()
        room_rules = context.get("generic", {}).get("room", [])
        room_rules += [
            rule
            for rule in context.get("specific", {}).get("rooms", [])
            if str(rule.get("target")) == str(room_id)
        ]
        return room_rules[query.offset:] if query.limit is None else room_rules[query.offset : query.offset + query.limit]
