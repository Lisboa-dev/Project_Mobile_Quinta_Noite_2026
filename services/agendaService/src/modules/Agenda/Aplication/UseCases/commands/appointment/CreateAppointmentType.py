from src.modules.agenda.aplication.ports.events.BusPort import BusPort
from src.modules.agenda.aplication.ports.repository import AppointmentRepositoryPort
from src.modules.agenda.domain.valueObjects import AppointmentType
from src.modules.agenda.aplication.dtos.useCase.command.AppointmentUseCasesDTO import CreateAppointmentTypeCommand
from src.modules.agenda.aplication.dtos.exceptions import CreateUseCaseException
from src.modules.agenda.aplication.dtos.useCase.output import UseCaseOutputDTO
from src.modules.agenda.aplication.events.AppointmentEvent import AppointmentTypeCreatedEvent
from src.modules.agenda.aplication.useCases._context import command_to_context


class CreateAppointmentTypeUseCase:
    def __init__(self, repository: AppointmentRepositoryPort, bus: BusPort):
        self._repository = repository
        self.bus = bus
        
    async def execute(self, command: CreateAppointmentTypeCommand) -> UseCaseOutputDTO:
        try:
            appointment_type = AppointmentType(
                name=command.name,
                duration=command.duration,
                description=command.description,
            )

            if not isinstance(appointment_type, AppointmentType):
                return UseCaseOutputDTO.fail(
                    use_case=self.__class__.__name__,
                    action="create",
                    resource="appointment_type",
                    resource_id=command.name,
                    triggered_by_id=command.triggered_by_id,
                    message="Appointment type could not be created",
                )

            await self._repository.saveType(appointment_type)
            event = AppointmentTypeCreatedEvent(
                triggered_by_id=command.triggered_by_id,
                name=command.name,
                duration=command.duration,
                description=command.description,
            )
            await self.bus.emit(event)
            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="appointment_type",
                resource_id=command.name,
                triggered_by_id=command.triggered_by_id,
                event_name=event.EVENT_NAME,
            )

        except Exception as exc:
            raise CreateUseCaseException(
                code="CREATE_APPOINTMENT_TYPE_ERROR",
                message="Error creating appointment type",
                use_case=self.__class__.__name__,
                context={"command": command_to_context(command)},
                original=exc,
            ) from exc
