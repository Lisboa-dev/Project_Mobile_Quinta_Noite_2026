
from src.modules.agenda.aplication.events.PatientEvent import CreatePatientEvent
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import PatientRepositoryPort
from src.modules.agenda.aplication.dtos.useCase.command.PatientUseCasesDTO import CreatePatientCommand
from src.modules.agenda.domain.entities.Patient import Patient


class CreatePatientUseCase:
    def __init__(self, repository: PatientRepositoryPort, bus: BusPort):
        self.repository = repository
        self._bus = bus
    
    async def execute(self, command: CreatePatientCommand) -> UseCaseOutputDTO:
       
       try:
            pacient = Patient(id=command.id, name=command.name)
            
            await self.repository.save(pacient)
            event = CreatePatientEvent.from_entity(pacient, triggered_by_id=command.triggered_by_id)
            await self._bus.emit(event)
            
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="patient",
                resource_id=str(pacient.id),
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
            
       except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="create",
                resource="patient",
                resource_id=command.id,
                triggered_by_id=command.triggered_by_id,
                message=str(e),
            )
