from enum import Enum

class CargoEnum(Enum):
    MEDICO = "MEDICO"
    ATENDENTE = "ATENDENTE"
    GERENTE = "GERENTE"
    SUPERVISOR = "SUPERVISOR"
    PACIENTE = "PACIENTE"  # default

class Cargo:
    def __init__(self, valor: str|None):
       if (valor==None): 
           self.valor=None
       else:
           if(valor in CargoEnum):
             self.valor = valor

    def __str__(self):
        return self.valor.value

    def __repr__(self):
        return f"CargoVO({self.valor})"