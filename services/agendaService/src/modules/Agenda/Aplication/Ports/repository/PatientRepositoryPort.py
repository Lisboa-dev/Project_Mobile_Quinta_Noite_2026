
from abc import ABC, abstractmethod
from typing import Any
from src.modules.agenda.domain.entities.Patient import Patient

class PatientRepositoryPort(ABC):
    @abstractmethod
    async def save(self, patient: Patient) -> None:
        pass
    
    @abstractmethod
    async def update(self, patient: Patient) -> None:
        pass
    
    async def delete(self, patient_id: str) -> None:
        pass

    async def getPacient(self, patient_id: str) -> Any:
        pass

    async def getPatient(self, patient_id: str) -> Any:
        return await self.getPacient(patient_id)
