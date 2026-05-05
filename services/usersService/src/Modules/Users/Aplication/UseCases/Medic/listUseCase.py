from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iMedicRepository import IMedicRepository 
from Users.Domain.Entities.medicEntity import  Medic

class ListUserUseCase:

    def __init__(self, repository: IMedicRepository):
        self.repository = repository

    def execute(self):
        try:
            listUser = self.repository.find_all()
            return listUser
        except Exception as e:
            raise Exception("Erro ao encontar a lista de medicos", e)