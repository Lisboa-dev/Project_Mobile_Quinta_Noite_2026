from ..ValueObjects.cargoVO import  Cargo
from ..ValueObjects.userNomeVO import UserName
from ..ValueObjects.emailVO import Email
from ..ValueObjects.roleVO import  Role
from ..ValueObjects.passwordVO import Password
from ..ValueObjects.NomeVO import Nome



class SoftPacient:
    def __init__(self, userName:str, email: Email, nome:str=None, password:str=None,cargo:str = None, role: str =None):
        self.userName = UserName(userName)
        self.nome = Nome(nome)
        self.email = Email(email)
        self.password = Password(password)
        self.cargo = Cargo(cargo)
        self.role = Role(role)

    def __repr__(self):
        return f"User(nome={self.nome}, email={self.email}, cargo={self.cargo}, role={self.role})"

    def __str__(self):
        return f"{self.nome} <{self.email}> - {self.cargo} / {self.role}"
    
    