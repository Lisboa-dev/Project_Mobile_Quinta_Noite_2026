from ....dtos.useCase.command import DepreciatUserCommand
from ....dtos.useCase.output import UseCaseOutputDTO
from ....events.adminEvents import UserDepreciatEvent
from ....ports.events import EventBusPort
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await, read_value, user_event_payload


class DepreciatUserUseCase:
    def __init__(self, repository: UserRepositoryPort, event_bus: EventBusPort):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, command: DepreciatUserCommand):
        user = await maybe_await(self._repository.find_by_id(command.id))
        if user is None:
            raise UserNotFoundException(command.id)

        previous_cargo = read_value(getattr(user, "cargo", None))

        try:
            updated = await maybe_await(self._repository.update(command.id, {"cargo": "ATENDENTE"}))
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
        event = UserDepreciatEvent(
            **user_event_payload(
                updated,
                triggered_by_id=command.triggered_by_id,
                previous_cargo=previous_cargo,
                cargo="ATENDENTE",
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
            message="depreciacao processada com sucesso",
        )
