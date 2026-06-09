from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.events.RoomEvent import DeleteRoomEvent
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.domain.entities.Room import Room
from src.modules.agenda.aplication.ports.repository.RoomRepositoryPort import RoomRepositoryPort

class DeleteRoomUseCase:
    def __init__(self, repository: RoomRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus= bus
    async def execute(self, room_id: str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        try:
            room = await self._repository.getRoom(room_id)
            if not isinstance(room, Room):
                return UseCaseOutputDTO.fail(
                    use_case=self.__class__.__name__,
                    action="delete",
                    resource="room",
                    resource_id=room_id,
                    triggered_by_id=triggered_by_id,
                    message="Room not found",
                )
            roomEntity = Room(name = room.name, disponibility = room.disponibility, rules = room.rules)
            
            if(room and roomEntity.delete()):
                await self._repository.deleteRoom(room_id)
                event = DeleteRoomEvent(triggered_by_id=triggered_by_id, room_id=str(room_id))
                await self._bus.emit(event)
                return UseCaseOutputDTO.ok(
                    use_case=self.__class__.__name__,
                    action="deleted",
                    resource="room",
                    resource_id=str(room_id),
                    triggered_by_id=triggered_by_id,
                    event_name=event.EVENT_NAME,
                )
        
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="delete",
                resource="room",
                resource_id=room_id,
                triggered_by_id=triggered_by_id,
                message=str(e),
            )
        return UseCaseOutputDTO.fail(
            use_case=self.__class__.__name__,
            action="delete",
            resource="room",
            resource_id=room_id,
            triggered_by_id=triggered_by_id,
            message="Room could not be deleted",
        )
       
