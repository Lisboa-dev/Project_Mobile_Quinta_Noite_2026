
from src.modules.agenda.aplication.dtos.useCase.command.RoomUseCasesDTO import UpdateRoomCommand
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.RoomEvent import UpdateRoomEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository.RoomRepositoryPort import RoomRepositoryPort


class UpdateRoomUseCase:
    def __init__(self, repository: RoomRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus= bus
    
    async def execute(self, Imput:UpdateRoomCommand) -> UseCaseOutputDTO:
         room = await self._repository.getRoom(Imput.id)
         if not isinstance(room, object) or not hasattr(room, "updateStateRoom"):
             return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="update",
                resource="room",
                resource_id=Imput.id,
                triggered_by_id=Imput.triggered_by_id,
                message="Room not found",
             )
         roomUpdated = room.updateStateRoom(Imput)
         
         if(roomUpdated and await self._repository.update(roomUpdated)):
             event = UpdateRoomEvent.from_entity(roomUpdated, triggered_by_id=Imput.triggered_by_id)
             await self._bus.emit(event)
             return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="updated",
                resource="room",
                resource_id=str(roomUpdated.id),
                triggered_by_id=Imput.triggered_by_id,
                event_name=event.EVENT_NAME,
             )
         
         return UseCaseOutputDTO.fail(
            use_case=self.__class__.__name__,
            action="update",
            resource="room",
            resource_id=Imput.id,
            triggered_by_id=Imput.triggered_by_id,
            message="Room update was not persisted",
         )
