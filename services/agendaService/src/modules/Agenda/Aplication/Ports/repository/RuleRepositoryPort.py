from abc import ABC, abstractmethod
from typing import Any
from src.modules.agenda.domain.rules.BaseRule import BaseRule

class RuleRepositoryPort(ABC):
    
    @abstractmethod
    async def save(self, rule: BaseRule) -> None:
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> None:
        pass

    async def deleteRule(self, rule_id: str) -> Any:
        await self.delete(rule_id)
        return True

    async def getDayRules(self) -> list[Any]:
        return []
