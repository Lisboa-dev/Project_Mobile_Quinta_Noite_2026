from src.modules.agenda.domain.entities.Room import Room
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RoomEvent import CreateRoomEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository.RoomRepositoryPort import RoomRepositoryPort


class CreateRoomUseCase:
    def __init__(self, repository: RoomRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, name: str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        try:
            rules=await self._repository.getGenericRulesRoom()
            room = Room(name=name, rules=rules)
            if isinstance(room,Room):
             await self._repository.save(room) 
             event = CreateRoomEvent.from_entity(room, triggered_by_id=triggered_by_id)
             await self._bus.emit(event)
             return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="room",
                resource_id=str(room.id),
                triggered_by_id=triggered_by_id,
                event_name=event.EVENT_NAME,
             )
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="create",
                resource="room",
                triggered_by_id=triggered_by_id,
                message="Room entity could not be created",
            )
        
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_ROOM_ERROR",
                message="Error creating room",
                use_case=self.__class__.__name__,
                context={"name": name, "triggered_by_id": triggered_by_id},
                original=e,
            ) from e
