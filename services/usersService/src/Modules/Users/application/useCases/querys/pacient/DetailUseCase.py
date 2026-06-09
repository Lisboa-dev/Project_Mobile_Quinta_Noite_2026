from ....dtos.useCase.output import UserOutputDTO
from ....dtos.useCase.querys import GetUserByIdQuery
from ....ports.repository import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await


class DetailPacientUseCase:
    def __init__(self, repository: UserRepositoryPort):
        self._repository = repository

    async def execute(self, query: GetUserByIdQuery | int) -> UserOutputDTO:
        pacient_id = query.id if isinstance(query, GetUserByIdQuery) else query
        pacient = await maybe_await(self._repository.find_by_id(pacient_id))
        if pacient is None:
            raise UserNotFoundException(pacient_id)
        return UserOutputDTO.from_entity(pacient)
