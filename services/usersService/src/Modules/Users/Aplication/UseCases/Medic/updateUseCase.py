from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iMedicRepository import IMedicRepository 
from Users.Domain.Entities.medicEntity import  Medic
from services.usersService.src.Modules.Users.Aplication.DTOs.commands.updateMedicDTO import UpdateMedicDTO

class UpdateUserUseCase:

    def __init__(self, repository: IMedicRepository):
        self.repository = repository

    def execute(self, id:int, data:UpdateMedicDTO):
       try: # Lógica para criar uma agenda
            values=Medic.to_object(data)
            if values and values != "":
                updateAproved = values.to_dict()
            response = self.repository.update(id, updateAproved)
            if response: 
                return True
            return "dados inválidos"
       except Exception as e:
           raise Exception("", e)