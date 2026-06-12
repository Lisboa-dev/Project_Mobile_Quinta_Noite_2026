
from abc import ABC, abstractmethod
from typing import Any
from src.modules.agenda.domain.entities.Room import Room

class RoomRepositoryPort(ABC):
    async def save(self, room: Room) -> None:
       pass
   
    async def update(self, room: Room) -> bool:
       return False
   
    async def delete(self, room_id: str) -> None:
       pass

    async def getRoom(self, room_id: str) -> Any:
       pass

    async def deleteRoom(self, room_id: str) -> None:
       await self.delete(room_id)

    async def getGenericRulesRoom(self) -> list[Any]:
       return []
