from....ports.events import EventBusPort
from....ports.repository.UserRepositoryPort import UserRepositoryPort
from ....dtos.useCase.command import CreatePacientCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.pacientEvents import PacientCreatedEvent
from .....domain.entities.PacientEntity import Pacient
from .....domain.exceptions.DomainExceptions import UserAlreadyExistsException
from .._helpers import maybe_await, read_value, user_event_payload


class CreatePacientUseCase:
    def __init__(self, repository: UserRepositoryPort, event_bus: EventBusPort):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, command: CreatePacientCommand):
        pacient = Pacient.create_user(
            userName=command.userName,
            email=command.email,
            name=command.name,
            password=command.password,
            cpf=command.cpf,
        )

        if await maybe_await(self._repository.find_by_username(pacient.userName.value)):
            raise UserAlreadyExistsException("userName")
        if await maybe_await(self._repository.find_by_email(pacient.email.value)):
            raise UserAlreadyExistsException("email")

        try:
            saved = await maybe_await(self._repository.save(pacient))
            event = PacientCreatedEvent(
                **user_event_payload(
                    saved,
                    triggered_by_id=command.triggered_by_id,
                    cpf=getattr(saved, "cpf", command.cpf),
                )
            )
            await maybe_await(self._event_bus.publish(event))
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="created",
                resource="pacient",
                resource_id=str(read_value(getattr(pacient, "id", None))),
                triggered_by_id=command.triggered_by_id,
                message=str(e),
            )

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="created",
            resource="pacient",
            resource_id=str(read_value(getattr(saved, "id", None))),
            triggered_by_id=command.triggered_by_id,
            event_name=event.__class__.__name__,
            message="criacao de paciente processada com sucesso",
        )
