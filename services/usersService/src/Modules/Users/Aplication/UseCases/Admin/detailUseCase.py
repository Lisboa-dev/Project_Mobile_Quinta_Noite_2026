from ...Repository.iAgendaRepository import IUserRepository 
from ...Domain.Entities.userEntity import  User
class DetailUserUseCase:

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, id:int):
        # Lógica para criar uma agenda
        user = self.repository.find_by_id(id)
        return user