from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iMedicRepository import IMedicRepository 
from Users.Domain.Entities.medicEntity import  Medic


class DeleteUserUseCase:

    def __init__(self, repository: IMedicRepository):
        self.repository = repository

    def execute(self, id:int):
        try:
          medic = self.repository.find_by_id(id)
          if not medic:
              raise Exception("Médico não encontrado")
          obj = Medic.to_object(medic)
          if obj.destroy():
           self.repository.delete(id)
           return
           
        except Exception as e:
            raise Exception("", e)
        return False
       