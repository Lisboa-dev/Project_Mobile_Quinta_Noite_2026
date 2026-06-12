from abc import ABC, abstractmethod
from typing import Any


class AppointmentRepositoryPort(ABC):
    @abstractmethod
    async def save(self, appointment: Any, scheduler_id: str | None = None) -> None:
        pass

    @abstractmethod
    async def update(self, appointment: Any) -> None:
        pass

    @abstractmethod
    async def delete(self, appointment_id: str) -> None:
        pass

    @abstractmethod
    async def get(self, appointment_id: str) -> Any:
        pass

    async def getAppointment(self, id: str) -> Any:
        return await self.get(id)

    async def saveType(self, appointment_type: Any) -> None:
        pass
