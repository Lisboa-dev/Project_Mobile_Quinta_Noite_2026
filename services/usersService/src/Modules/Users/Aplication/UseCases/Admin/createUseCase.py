from ...Repository.iAgendaRepository import IUserRepository 
from ...Domain.Entities.userEntity import  User
class CreateUserUseCase:

    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def execute(self, data:Create):
        # Lógica para criar uma agenda
        user = User(data.userName, data.email, data.name, data.password) 
        new_user = user.__getattribute__
        self.repository.save(new_user)
        
        return 
    
    
    