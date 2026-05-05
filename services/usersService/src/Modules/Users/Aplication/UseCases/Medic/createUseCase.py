from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iMedicRepository import IMedicRepository 
from Users.Domain.Entities.medicEntity import  Medic
from services.usersService.src.Modules.Users.Aplication.DTOs.commands.createMedicDTO import CreateMedicDTO


class CreateMedicUseCase:

    def __init__(self, repository: IMedicRepository):
        self.repository = repository

    def execute(self, data:CreateMedicDTO):
        # Lógica para criar um medico
        try:
            medico = Medic(data.userName, data.email, data.name, data.password) 
            new_user = medico.to_dict()
            if new_user != None and self.repository.find_by_username(new_user['userName']) == None and self.repository.find_by_email(new_user['email']) == None: 
              self.repository.save(new_user)
            return("Médico já existe")
        except Exception as e:
            print(f"Erro ao criar médico: {e}")
            raise e
        
        
        
       
    
    
    