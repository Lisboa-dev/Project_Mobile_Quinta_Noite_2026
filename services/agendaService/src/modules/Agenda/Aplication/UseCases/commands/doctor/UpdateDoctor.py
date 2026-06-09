



from src.modules.agenda.aplication.dtos.useCase.command.DoctorUseCasesDTO import UpdateDoctorCommand
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.DoctorEvent import UpdateDoctorEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import DoctorRepositoryPort


class UpdateDoctorUseCase:
    
    def __init__(self, repository:DoctorRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, data:UpdateDoctorCommand) -> UseCaseOutputDTO:
        
        doctor = await self._repository.get(data)
        
        if doctor:
            event = UpdateDoctorEvent.from_entity(doctor, triggered_by_id=data.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="updated",
                resource="doctor",
                resource_id=str(doctor.id),
                triggered_by_id=data.triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        
        return UseCaseOutputDTO.fail(
            use_case=self.__class__.__name__,
            action="update",
            resource="doctor",
            resource_id=data.id,
            triggered_by_id=data.triggered_by_id,
            message="Doctor not found",
        )
