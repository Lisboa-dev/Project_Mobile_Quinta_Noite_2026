from .userEntity import User

class Medic(User):
    def __init__(self, userName:str, email: str, nome:str=None, password:str=None):
        super().__init__(userName, email, nome, password, cargo="Medico")
        
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
            "userName": self.userName.value,    
        }
        
    @classmethod
    @staticmethod
    def to_object(cls, **kwargs):
        if kwargs.get("userName") != None and kwargs.get("userName") != "":
             userName=kwargs.get("userName")
        if kwargs.get("email") != None and kwargs.get("email") and kwargs.get("email") != "":
            email=kwargs.get("email") 
        if kwargs.get("name") != None and kwargs.get("name") != "":  
            name=kwargs.get("name")
        
        return cls(
            userName=userName,
            email=email,
            name=name,
        )
    
    
    def update(self, name:str=None, cargo:str = None, userName:str=None, email:str=None, password:str=None):
        return super().update(name, cargo, userName, email, password)
    
    def destroy(self) ->bool:
        return True
    
 