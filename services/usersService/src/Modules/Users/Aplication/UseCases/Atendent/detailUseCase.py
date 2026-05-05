from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iAtendenteRepository import IAtendenteRepository 
from Users.Domain.Entities.atendenteEntity import  Atendente

class DetailUserUseCase:

    def __init__(self, repository: IAtendenteRepository):
        self.repository = repository

    def execute(self, id:int):
        # Lógica para criar uma agenda
        try:
         user = self.repository.find_by_id(id)
         return user
        except Exception as e:
            raise Exception("", e)
     
    
    