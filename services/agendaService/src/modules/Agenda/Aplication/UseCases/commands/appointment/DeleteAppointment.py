

from src.modules.agenda.aplication.dtos.useCase.command.AppointmentUseCasesDTO import DeleteAppointmentCommand
from src.modules.agenda.aplication.dtos.exceptions import DeleteUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.AppointmentEvent import AppointmentDeletedEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import AppointmentRepositoryPort


class DeleteAppointmentUseCase:
    def __init__(self, repository: AppointmentRepositoryPort, bus: BusPort):
        self._repository = repository
        self.bus = bus
        
    async def execute(self, command: DeleteAppointmentCommand) -> UseCaseOutputDTO:
        try:
            await self._repository.delete(command.id)
            event = AppointmentDeletedEvent(triggered_by_id=command.triggered_by_id, appointment_id=command.id)
            await self.bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="appointment",
                resource_id=command.id,
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        except Exception as e:
            raise DeleteUseCaseException(
                code="DELETE_APPOINTMENT_ERROR",
                message="Error deleting appointment",
                use_case=self.__class__.__name__,
                context={"appointment_id": command.id},
                original=e,
            ) from e
