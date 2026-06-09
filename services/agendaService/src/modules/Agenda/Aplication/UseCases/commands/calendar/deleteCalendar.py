from src.modules.agenda.aplication.dtos.exceptions import DeleteUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.CalendarEvent import DeleteCalendarEvent
from src.modules.agenda.aplication.ports.repository.CalendarRepositoryPort import CalendarRepositoryPort


class DeleteCalendarUseCase:
    def __init__(self, repository: CalendarRepositoryPort, bus=None):
        self._repository = repository
        self.bus = bus
    
    async def execute(self, ano:str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        try:
            await self._repository.delete(ano) 
            if self.bus:
                event = DeleteCalendarEvent(triggered_by_id=triggered_by_id, year=str(ano))
                await self.bus.emit(event)
                event_name = event.EVENT_NAME
            else:
                event_name = None
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="calendar",
                resource_id=str(ano),
                triggered_by_id=triggered_by_id,
                event_name=event_name,
            )
        except Exception as e:
            raise DeleteUseCaseException(
                code="DELETE_CALENDAR_ERROR",
                message="Error deleting calendar",
                use_case=self.__class__.__name__,
                context={"year": ano},
                original=e,
            ) from e
