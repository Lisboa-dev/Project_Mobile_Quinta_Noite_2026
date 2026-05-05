from enum import Enum

class RoleEnum(Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"
    FUNCIONARIO = "FUNCIONARIO"
    MEDICO = "MEDICO"

class Role:
    def __init__(self, valor: str|None):
       if (valor==None): 
           self.valor=None
       else:
           if(valor in RoleEnum):
             self.valor = valor
             
             
    def __str__(self):
        return self.valor.value

    def __repr__(self):
        return f"RoleVO({self.valor})"