from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iAtendenteRepository import IAtendenteRepository 
from Users.Domain.Entities.atendenteEntity import  Atendente

class UpdateUserUseCase:

    def __init__(self, repository: IAtendenteRepository):
        self.repository = repository

    def execute(self, id:int, data:dict):
       try: # Lógica para criar uma agenda
            values=Atendente.to_object(data)
            if values and values != "":
                updateAproved = values.to_dict()
            response = self.repository.update(id, updateAproved)
            if response: 
                return True
            return "dados inválidos"
       except Exception as e:
           raise Exception("", e)

