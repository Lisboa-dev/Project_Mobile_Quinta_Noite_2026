from ....dtos.useCase.output import UserOutputDTO
from ....dtos.useCase.querys import ListUsersQuery
from ....ports.repository import UserRepositoryPort
from .._helpers import maybe_await


class ListMedicUseCase:
    def __init__(self, repository: UserRepositoryPort):
        self._repository = repository

    async def execute(self, query: ListUsersQuery | None = None) -> list[UserOutputDTO]:
        query = query or ListUsersQuery()
        medics = await maybe_await(self._repository.find_all())
        start = max(query.offset, 0)
        end = start + query.limit if query.limit is not None else None
        return [UserOutputDTO.from_entity(medic) for medic in medics[start:end]]
