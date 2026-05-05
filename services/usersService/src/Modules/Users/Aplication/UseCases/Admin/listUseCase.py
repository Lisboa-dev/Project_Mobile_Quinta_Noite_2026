from ...Repository.iAgendaRepository import IUserRepository 
from ...Domain.Entities.userEntity import  User
class ListUserUseCase:

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self):
       listUser = self.repository.find_all()
       return listUser