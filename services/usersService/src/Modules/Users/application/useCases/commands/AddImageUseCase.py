from ...dtos.useCase.command import AddImageCommand
from ...dtos.useCase.output import UseCaseOutputDTO, UserOutputDTO
from ...events import UserProfileImageAddedEvent
from ...ports.events import EventBusPort
from ...ports.repository import UserRepositoryPort
from ....domain.exceptions.DomainExceptions import UserNotFoundException
from ._helpers import maybe_await, read_value, user_event_payload


class AddImageUseCase:
    def __init__(self, repository: UserRepositoryPort, event_bus: EventBusPort):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, command: AddImageCommand) -> UseCaseOutputDTO:
        user = await maybe_await(self._repository.find_by_id(command.user_id))
        if user is None:
            raise UserNotFoundException(command.user_id)

        previous_object = getattr(user, "profile_image_object", None)
        updated = await maybe_await(
            self._repository.update(
                command.user_id,
                {
                    "profile_image_url": command.image_url,
                    "profile_image_object": command.image_object,
                },
            )
        )
        if updated is None:
            raise UserNotFoundException(command.user_id)

        event = UserProfileImageAddedEvent(
            **user_event_payload(
                updated,
                triggered_by_id=command.triggered_by_id,
                profile_image_url=command.image_url,
                profile_image_object=command.image_object,
                previous_profile_image_object=previous_object,
            )
        )
        await maybe_await(self._event_bus.publish(event))
        user_output = UserOutputDTO.from_entity(updated)

        return UseCaseOutputDTO.ok(
            use_case=self.__class__.__name__,
            action="updated",
            resource="user_profile_image",
            resource_id=str(read_value(command.user_id)),
            triggered_by_id=command.triggered_by_id,
            event_name=event.__class__.__name__,
            message="imagem de perfil atualizada com sucesso",
            data={
                "user": user_output.to_dict(),
                "previous_profile_image_object": previous_object,
            },
        )
