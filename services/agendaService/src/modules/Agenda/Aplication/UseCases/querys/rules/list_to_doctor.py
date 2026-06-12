from typing import Any

from src.modules.agenda.aplication.dtos.useCase.query import ListQuery


class ListRulesToDoctorUseCase:
    def __init__(self, repository):
        self._repository = repository

    async def execute(self, doctor_id: str, query: ListQuery) -> list[dict[str, Any]]:
        context = await self._repository.admin_context()
        doctor_rules = context.get("generic", {}).get("doctor", [])
        doctor_rules += [
            rule
            for rule in context.get("specific", {}).get("doctors", [])
            if str(rule.get("target")) == str(doctor_id)
        ]
        return doctor_rules[query.offset:] if query.limit is None else doctor_rules[query.offset : query.offset + query.limit]
