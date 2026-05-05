from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iAtendenteRepository import IAtendenteRepository 
from Users.Domain.Entities.atendenteEntity import  Atendente


class DeleteUserUseCase:

    def __init__(self, repository: IAtendenteRepository):
        self.repository = repository

    def execute(self, id:int):
        try:
          atendente = self.repository.find_by_id(id)
          if not atendente:
              raise Exception("atendente não encontrado")
          obj = Atendente.to_object(atendente)
          if obj.destroy():
           self.repository.delete(id)
           return
           
        except Exception as e:
            raise Exception("", e)
        return False
       