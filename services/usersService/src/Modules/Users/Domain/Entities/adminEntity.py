from .userEntity import User

class Admin(User):
    def __init__(self, userName:str, email: str, nome:str=None, password:str=None):
        super().__init__(userName, email, nome, password, cargo="Admin")
        
    def __setattr__(self, name, value):
        return super().__setattr__(name, value) 
    
    def __getattribute__(self, att):
        return super().__getattribute__(att)
    
    def __repr__(self):
        return f"User(nome={self.nome}, email={self.email}, cargo={self.cargo}, role={self.role})"
    
    def __str__(self):
        return f"{self.nome} <{self.email}> - {self.cargo}"
    
    def to_dict(self):
        return {
            
        }