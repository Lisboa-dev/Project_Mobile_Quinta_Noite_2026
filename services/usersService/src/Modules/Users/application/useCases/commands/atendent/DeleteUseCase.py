from ....dtos.useCase.command import DeleteAtendenteCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.atendentEvents import AtendentDeletedEvent
from ....ports.events.EventBusPort import EventBusPort
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await, read_value, user_event_payload


class DeleteAtendentUseCase:
    def __init__(self, repository: UserRepositoryPort, event_bus: EventBusPort):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, command: DeleteAtendenteCommand) -> UseCaseOutputDTO:
        current = await maybe_await(self._repository.find_by_id(command.id))
        if current is None:
            raise UserNotFoundException(command.id)

        try:
            await maybe_await(self._repository.delete(command.id))
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="deleted",
                resource="atendent",
                resource_id=str(command.id),
                triggered_by_id=command.triggered_by_id,
                message=str(e),
            )

        event = AtendentDeletedEvent(**user_event_payload(current, triggered_by_id=command.triggered_by_id))
        await maybe_await(self._event_bus.publish(event))

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="deleted",
            resource="atendent",
            resource_id=str(read_value(command.id)),
            triggered_by_id=command.triggered_by_id,
            event_name=event.__class__.__name__,
            message="delecao de atendente processada com sucesso",
        )


DeleteAtendenteUseCase = DeleteAtendentUseCase
