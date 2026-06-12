
from abc import ABC, abstractmethod
from src.modules.agenda.domain.rules.BaseRule import BaseRule


class CalendarDataPort(ABC):

    @abstractmethod
    def pullData(self) -> list[BaseRule]:
        pass

    async def mont(self, mes: int | str, ano: int | str) -> list[dict]:
        return []
