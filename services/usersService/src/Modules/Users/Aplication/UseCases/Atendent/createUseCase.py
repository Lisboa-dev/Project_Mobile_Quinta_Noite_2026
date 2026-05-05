from services.usersService.src.Modules.Users.Aplication.Ports.Repository.iAtendenteRepository import IAtendenteRepository 
from Users.Domain.Entities.atendenteEntity import  Atendent
from services.usersService.src.Modules.Users.Aplication.DTOs.commands.createAtendenteDTO import CreateAtendenteDTO


class CreateAtendentUseCase:

    def __init__(self, repository: IAtendenteRepository):
        self.repository = repository

    def execute(self, data:CreateAtendenteDTO):
        # Lógica para criar um Atendento
        try:
            Atendento = Atendent(data.userName, data.email, data.name, data.password) 
            new_user = Atendento.to_dict()
            if new_user != None and self.repository.find_by_username(new_user['userName']) == None and self.repository.find_by_email(new_user['email']) == None: 
              self.repository.save(new_user)
            return("Pacient já existe")
        except Exception as e:
            print(f"Erro ao criar Pacient: {e}")
            raise e
        
        
        
       
    
    
    