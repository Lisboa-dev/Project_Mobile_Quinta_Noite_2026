


from src.modules.agenda.aplication.events.DoctorEvent import DeleteDoctorEvent
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import DoctorRepositoryPort


class DeleteDoctorUseCase:
    
    def __init__(self, repository:DoctorRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, doctor_id: str, triggered_by_id: str | None = None) -> UseCaseOutputDTO:
        doctor = await self._repository.getDoctor(doctor_id)
        if doctor:
            await self._repository.delete(doctor_id)
            event = DeleteDoctorEvent(triggered_by_id=triggered_by_id, doctor_id=doctor_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="doctor",
                resource_id=doctor_id,
                triggered_by_id=triggered_by_id,
                event_name=event.EVENT_NAME,
            )
        return UseCaseOutputDTO.fail(
            use_case=self.__class__.__name__,
            action="delete",
            resource="doctor",
            resource_id=doctor_id,
            triggered_by_id=triggered_by_id,
            message="Doctor not found",
        )
