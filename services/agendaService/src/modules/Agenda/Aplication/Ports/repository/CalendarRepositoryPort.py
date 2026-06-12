
from abc import ABC, abstractmethod

from typing import Any
from src.modules.agenda.domain.entities import Day

class CalendarRepositoryPort (ABC):
   
   @abstractmethod
   async def save(self, calendar: Any) -> None:
       pass

   async def saveMany(self, days: list[Day]) -> None:
       for day in days:
           await self.save(day)
   
   @abstractmethod
   async def update(self, calendar: Any) -> None:
       pass
   
   @abstractmethod
   async def delete(self, ano: str | int | None = None) -> None:
       pass
   
   @abstractmethod
   async def updateDay(self, day: Day) -> None:
       pass

   async def get(self, day_id: str) -> Any:
       pass
