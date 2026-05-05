from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iAtendenteRepository import IAtendenteRepository 
from Users.Domain.Entities.atendenteEntity import  Atendente

class ListUserUseCase:

    def __init__(self, repository: IAtendenteRepository):
        self.repository = repository

    def execute(self):
        try:
            listUser = self.repository.find_all()
            return listUser
        except Exception as e:
            raise Exception("Erro ao encontar a lista de Atendentos", e)
   
   
   