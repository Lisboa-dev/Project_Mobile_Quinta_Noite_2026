from abc import ABC, abstractmethod

from ..ValueObjects.cargoVO import  Cargo
from ..ValueObjects.userNomeVO import UserName
from ..ValueObjects.emailVO import Email
from ..ValueObjects.passwordVO import Password
from ..ValueObjects.nomeVO import Nome



class User(ABC):
    def __init__(self, userName:str, email: str, name:str, password:str=None,cargo:str = None):
        self.userName = UserName(userName)
        self.nome = Nome(name)
        self.email = Email(email)
        if password!= None:
         self.password = Password(password)
        self.cargo = Cargo(cargo)
        

    def __repr__(self):
        
        return f"User(nome={self.nome}, email={self.email}, cargo={self.cargo}, role={self.role})"

    def __str__(self):
        return f"{self.nome} <{self.email}> - {self.cargo}"
    
    
    def update(self, name:str=None, cargo:str = None, userName:str=None, email:str=None):
        if name and name!= None and name.strip() != "":
            self.nome = Nome(name)
        if cargo and cargo!=None and cargo.strip()!= "":
            self.cargo = Cargo(cargo)
        if userName and userName!=None and userName.strip() != "":
            self.userName = UserName(userName)
        if email and email!=None and email.strip() != "":
            self.email = Email(email)
            
        return {
            "userName": self.userName.value,
            "nome": self.nome.value,
            "email": self.email.value,
            "cargo": self.cargo.value
        }
    
    @abstractmethod
    def to_dict(self):
        pass
    
    @abstractmethod
    def to_object(self):
        pass
        
        
    
    
    
    
    