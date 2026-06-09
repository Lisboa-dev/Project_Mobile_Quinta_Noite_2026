from dataclasses import dataclass
from src.modules.agenda.aplication.dtos.exceptions import UpdateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.CalendarEvent import UpdateDayEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository.CalendarRepositoryPort import CalendarRepositoryPort
from src.modules.agenda.domain.entities import Day


@dataclass(frozen=True)
class UpdateDayCommand:
    id: str
    data: dict
    triggered_by_id: str | None = None


class UpdateDayUseCase:
    def __init__(self, repository: CalendarRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, command: UpdateDayCommand) -> UseCaseOutputDTO:
        try:
            data = await self._repository.get(command.id)
            if not isinstance(data, Day):
                return UseCaseOutputDTO.fail(
                    use_case=self.__class__.__name__,
                    action="update",
                    resource="day",
                    resource_id=command.id,
                    triggered_by_id=command.triggered_by_id,
                    message="Day not found",
                )
            day = data
            dayUpdated = day.update(command.data)
            await self._repository.updateDay(dayUpdated)
            event = UpdateDayEvent.from_entity(dayUpdated, triggered_by_id=command.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="updated",
                resource="day",
                resource_id=str(dayUpdated.date),
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        except Exception as e:
            raise UpdateUseCaseException(
                code="UPDATE_DAY_ERROR",
                message="Error updating calendar day",
                use_case=self.__class__.__name__,
                context={"command": str(command)},
                original=e,
            ) from e
