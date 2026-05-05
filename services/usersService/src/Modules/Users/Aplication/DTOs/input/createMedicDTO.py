from typing import Protocol


#protocol que define os métodos que o controller deve implementar em tempo de desenvolvimento, sem precisar da implementação concreta
#use mypy para verificar se a classe que implementa o controller realmente implementa os métodos definidos na interface
#não existe em runtime, é apenas para verificação estática de tipos

class CreateMedicDTO(Protocol):
    name: str
    email: str
    password: str
    userName: str