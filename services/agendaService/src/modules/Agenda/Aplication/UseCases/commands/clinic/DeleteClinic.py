

from src.modules.agenda.aplication.events.ClinicEvent import DeleteClinicEvent
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import ClinicRepositoryPort


class DeleteClinicUseCase:
    def __init__(self, repository: ClinicRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, clinic: str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        clinic = await self._repository.getClinic(clinic)
        if clinic:
            clinic_id = str(clinic.id if hasattr(clinic, "id") else clinic)
            event = DeleteClinicEvent(triggered_by_id=triggered_by_id, clinic_id=clinic_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="clinic",
                resource_id=clinic_id,
                triggered_by_id=triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        return UseCaseOutputDTO.fail(
            use_case=self.__class__.__name__,
            action="delete",
            resource="clinic",
            resource_id=str(clinic),
            triggered_by_id=triggered_by_id,
            message="Clinic not found",
        )
