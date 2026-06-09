from ....dtos.useCase.command import PromoteUserCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.adminEvents import UserPromotedEvent
from ....ports.events import EventBusPort
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await, read_value, user_event_payload


class PromoteUserUseCase:
    def __init__(self, repository: UserRepositoryPort, eventBus: EventBusPort):
        self._repository = repository
        self._event_bus = eventBus

    async def execute(self, command: PromoteUserCommand):
        user = await maybe_await(self._repository.find_by_id(command.id))
        if user is None:
            raise UserNotFoundException(command.id)

        previous_cargo = read_value(getattr(user, "cargo", None))

        try:
            updated = await maybe_await(self._repository.update(command.id, {"cargo": "ADMIN"}))
        except Exception as e:
            return UseCaseOutputDTO.fail(
                use_case=self.__class__.__name__,
                action="updated",
                resource="user",
                resource_id=str(command.id),
                triggered_by_id=command.triggered_by_id,
                message=str(e),
            )

        updated = updated or user
        event = UserPromotedEvent(
            **user_event_payload(
                updated,
                triggered_by_id=command.triggered_by_id,
                previous_cargo=previous_cargo,
                cargo="ADMIN",
            )
        )
        await maybe_await(self._event_bus.publish(event))

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="updated",
            resource="user",
            resource_id=str(command.id),
            triggered_by_id=command.triggered_by_id,
            event_name=event.__class__.__name__,
            message="promocao de user processada com sucesso",
        )
