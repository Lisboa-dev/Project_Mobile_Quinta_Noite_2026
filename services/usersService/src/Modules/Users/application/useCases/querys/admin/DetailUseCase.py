from ....dtos.useCase.output import UserOutputDTO
from ....dtos.useCase.querys import GetUserByIdQuery
from ....ports.repository.UserRepositoryPort import UserRepositoryPort
from .....domain.exceptions.DomainExceptions import UserNotFoundException


class DetailAdminUseCase:
    def __init__(self, repository:UserRepositoryPort ):
        self._repository = repository

    def execute(self, query: GetUserByIdQuery | str) -> UserOutputDTO:
        admin_id = query.id if isinstance(query, GetUserByIdQuery) else str(query)
        admin = self._repository.find_by_id(admin_id)
        if admin is None:
            raise UserNotFoundException(admin_id)
        return UserOutputDTO.from_entity(admin)
