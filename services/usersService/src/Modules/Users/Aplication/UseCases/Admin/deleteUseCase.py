from ...Repository.iAgendaRepository import IUserRepository 
from ...Domain.Entities.userEntity import  User
class DeleteUserUseCase:

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, id:int):
        self.repository.delete(id)
        return 