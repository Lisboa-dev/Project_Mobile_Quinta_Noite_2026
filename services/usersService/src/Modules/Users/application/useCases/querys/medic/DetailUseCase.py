from ....dtos.useCase.output import UserOutputDTO
from ....dtos.useCase.querys import GetUserByIdQuery
from ....ports.repository import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException
from .._helpers import maybe_await


class DetailMedicUseCase:
    def __init__(self, repository: UserRepositoryPort):
        self._repository = repository

    async def execute(self, query: GetUserByIdQuery | str) -> UserOutputDTO:
        medic_id = query.id if isinstance(query, GetUserByIdQuery) else str(query)
        medic = await maybe_await(self._repository.find_by_id(medic_id))
        if medic is None:
            raise UserNotFoundException(medic_id)
        return UserOutputDTO.from_entity(medic)
