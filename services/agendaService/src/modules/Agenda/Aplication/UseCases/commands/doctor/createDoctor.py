
from src.modules.agenda.aplication.dtos.useCase.command.DoctorUseCasesDTO import CreateDoctorCommand
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.DoctorEvent import CreateDoctorEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import DoctorRepositoryPort
from src.modules.agenda.domain.entities import Doctor



class CreateDoctorUseCase:
    
    def __init__(self, repository:DoctorRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
        
    async def execute(self, data:CreateDoctorCommand) -> UseCaseOutputDTO:
      try:
        basicRules = await self._repository.GetDoctorGenericRules()
        doctor = Doctor(name=data.name, externId=data.id_extern, id=data.id_extern, rules=basicRules)
        
        if isinstance(doctor, Doctor):
            await self._repository.save(doctor)
            event = CreateDoctorEvent.from_entity(doctor, triggered_by_id=data.triggered_by_id)
            await self._bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="doctor",
                resource_id=str(doctor.id),
                triggered_by_id=data.triggered_by_id,
                event_name=event.EVENT_NAME,
                data={"extern_id": data.id_extern},
            )
        return UseCaseOutputDTO.fail(
            use_case=self.__class__.__name__,
            action="create",
            resource="doctor",
            triggered_by_id=data.triggered_by_id,
            message="Doctor entity could not be created",
        )
        
      except Exception as e:
        raise CreateUseCaseException(
            code="CREATE_DOCTOR_ERROR",
            message="Error creating doctor",
            use_case=self.__class__.__name__,
            context={"command": data.model_dump() if hasattr(data, "model_dump") else str(data)},
            original=e,
        ) from e
