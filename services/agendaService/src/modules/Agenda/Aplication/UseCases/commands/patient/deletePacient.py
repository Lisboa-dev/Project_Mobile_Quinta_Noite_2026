




from src.modules.agenda.aplication.events.PatientEvent import DeletePatientEvent
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import PatientRepositoryPort


class DeletePatientUseCase:
    def __init__(self, repository: PatientRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, id: str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        try:
            
            pacient = await self._repository.getPacient(id)
            if not pacient:
                return UseCaseOutputDTO.fail(
                    use_case=self.__class__.__name__,
                    action="delete",
                    resource="patient",
                    resource_id=id,
                    triggered_by_id=triggered_by_id,
                    message="Patient not found",
                )
            
            await self._repository.delete(id)
            event = DeletePatientEvent(triggered_by_id=triggered_by_id, patient_id=id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="patient",
                resource_id=id,
                triggered_by_id=triggered_by_id,
                event_name=event.EVENT_NAME,
            )
            
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="delete",
                resource="patient",
                resource_id=id,
                triggered_by_id=triggered_by_id,
                message=str(e),
            )
