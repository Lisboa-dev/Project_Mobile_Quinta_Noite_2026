
from abc import ABC, abstractmethod

from src.modules.agenda.aplication.dtos.repositorys.input.AppointmentSchedulingInputDTO import AppointmentSchedulingInputDTO
from src.modules.agenda.aplication.dtos.repositorys.output.AppointmentSchedulingOutputDTO import AppointmentSchedulingOutputDTO

class AppointmentSchedulingRepositoryPort (ABC):
   
    @abstractmethod
    async def getContext(self, appointmentScheduling: AppointmentSchedulingInputDTO) -> AppointmentSchedulingOutputDTO:
       pass
   
