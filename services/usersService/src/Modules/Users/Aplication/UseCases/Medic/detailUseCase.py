from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iMedicRepository import IMedicRepository 
from Users.Domain.Entities.medicEntity import  Medic

class DetailUserUseCase:

    def __init__(self, repository: IMedicRepository):
        self.repository = repository

    def execute(self, id:int):
        # Lógica para criar uma agenda
        try:
         user = self.repository.find_by_id(id)
         return user
        except Exception as e:
            raise Exception("", e)
     