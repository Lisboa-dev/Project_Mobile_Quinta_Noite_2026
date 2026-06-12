



from src.modules.agenda.aplication.dtos.useCase.command.ClinicUseCasesDTO import CreateClinicCommand
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.ClinicEvent import CreateClinicEvent
from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import ClinicRepositoryPort
from src.modules.agenda.domain.entities import Clinic


class CreateClinicUseCase:
    
    def __init__(self, repository: ClinicRepositoryPort, bus: BusPort):
        self._repository = repository
        self._bus = bus
    
    async def execute(self, command:CreateClinicCommand) -> UseCaseOutputDTO:
        # Lógica para criar um administrador
        try:
         clinic = Clinic(name=command.name, rules=command.rules)
         await self._repository.save(clinic)
         event = CreateClinicEvent.from_entity(clinic, triggered_by_id=command.triggered_by_id)
         await self._bus.emit(event)
        except Exception as e:
            raise CreateUseCaseException(
                code="CREATE_CLINIC_ERROR",
                message="Error creating clinic",
                use_case=self.__class__.__name__,
                context={"command": command.model_dump() if hasattr(command, "model_dump") else str(command)},
                original=e,
            ) from e
        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="created",
            resource="clinic",
            resource_id=str(clinic.id),
            triggered_by_id=command.triggered_by_id,
            event_name=event.EVENT_NAME,
        )
