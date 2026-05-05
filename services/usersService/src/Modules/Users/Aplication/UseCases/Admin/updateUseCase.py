from ...Repository.iAgendaRepository import IUserRepository 
from ...Domain.Entities.userEntity import  User
class UpdateUserUseCase:

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, id:int, data:dict):
        # Lógica para criar uma agenda
       response = self.repository.update(id, data)
       if response: 
           return True