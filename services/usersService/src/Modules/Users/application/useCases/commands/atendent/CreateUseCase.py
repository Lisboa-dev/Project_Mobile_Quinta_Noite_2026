from ....dtos.useCase.command import CreateAtendenteCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.atendentEvents import AtendentCreatedEvent
from ....ports.events.EventBusPort import EventBusPort
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .....domain.entities.AtendenteEntity import Atendente
from .....domain.exceptions.DomainExceptions import UserAlreadyExistsException
from .._helpers import maybe_await, read_value, user_event_payload


class CreateAtendentUseCase:
    def __init__(self, repository: UserRepositoryPort, event_bus: EventBusPort):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, data: CreateAtendenteCommand) -> UseCaseOutputDTO:
        atendent = Atendente.create_user(
            name=data.name,
            userName=data.userName,
            email=data.email,
            password=data.password,
            cpf=data.cpf,
        )

        if await maybe_await(self._repository.find_by_username(atendent.userName.value)):
            raise UserAlreadyExistsException("userName")
        if await maybe_await(self._repository.find_by_email(atendent.email.value)):
            raise UserAlreadyExistsException("email")

        try:
            saved = await maybe_await(self._repository.save(atendent))
            event = AtendentCreatedEvent(
                **user_event_payload(
                    saved,
                    triggered_by_id=data.triggered_by_id,
                    cpf=getattr(saved, "cpf", data.cpf),
                )
            )
            await maybe_await(self._event_bus.publish(event))
            resource_id = str(read_value(getattr(saved, "id", None)))

            return UseCaseOutputDTO.ok(
                use_case=self.__class__.__name__,
                action="created",
                resource="atendent",
                resource_id=resource_id,
                triggered_by_id=data.triggered_by_id,
                event_name=event.__class__.__name__,
                message="criacao de atendente processada com sucesso",
            )
        except Exception as e:
            raise Exception(e)


CreateAtendenteUseCase = CreateAtendentUseCase
