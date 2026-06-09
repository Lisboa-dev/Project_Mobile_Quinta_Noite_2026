
from abc import ABC, abstractmethod
from typing import Any
from src.modules.agenda.domain.entities.Doctor import Doctor


class DoctorRepositoryPort(ABC):
    @abstractmethod
    async def save(self, doctor: Doctor) -> None:
        pass
    
    @abstractmethod
    async def update(self, doctor: Doctor) -> None:
        pass
    
    @abstractmethod
    async def delete(self, doctor_id: str) -> None:
        pass
    async def getDoctor(self, doctor_id: str) -> Any:
        pass

    async def get(self, data: Any) -> Any:
        pass

    async def GetDoctorGenericRules(self) -> list[Any]:
        return []
