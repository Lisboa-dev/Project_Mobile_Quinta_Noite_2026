from abc import ABC, abstractmethod
from typing import Any
class ClinicRepositoryPort(ABC):
    
    @abstractmethod
    async def save(self, clinic: Any) -> None:
        pass
    
    async def update(self, clinic: Any) -> None:
        pass 
    
    async def delete(self, id: str) -> None:
        pass

    async def getClinic(self, clinic_id: str) -> Any:
        pass
