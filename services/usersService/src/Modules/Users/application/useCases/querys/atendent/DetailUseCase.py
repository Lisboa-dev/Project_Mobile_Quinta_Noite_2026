from ....dtos.useCase.output import UserOutputDTO
from ....dtos.useCase.querys import GetUserByIdQuery
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await


class DetailAtendentUseCase:
    def __init__(self, repository: UserRepositoryPort):
        self._repository = repository

    async def execute(self, query: GetUserByIdQuery | int) -> UserOutputDTO:
        atendent_id = query.id if isinstance(query, GetUserByIdQuery) else query
        atendent = await maybe_await(self._repository.find_by_id(atendent_id))
        if atendent is None:
            raise UserNotFoundException(atendent_id)
        return UserOutputDTO.from_entity(atendent)


DetailAtendenteUseCase = DetailAtendentUseCase
