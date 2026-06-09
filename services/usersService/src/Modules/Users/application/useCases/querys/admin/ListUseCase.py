from ....dtos.useCase.output import UserOutputDTO
from ....dtos.useCase.querys import ListUsersQuery
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .._helpers import maybe_await


class ListAdminUseCase:
    def __init__(self, repository: UserRepositoryPort):
        self._repository = repository

    async def execute(self, query: ListUsersQuery | None = None) -> list[UserOutputDTO]:
        query = query or ListUsersQuery()
        admins = await maybe_await(self._repository.find_all())
        start = max(query.offset, 0)
        end = start + query.limit if query.limit is not None else None
        return [UserOutputDTO.from_entity(admin) for admin in admins[start:end]]
