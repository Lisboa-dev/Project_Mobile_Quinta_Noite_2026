from services.notificacaoService.src.API.Interfaces import UseCasesAgendaInterface
from fastapi import APIRouter, Depends




class AgendaController:

    def __init__(self, usecase: UseCasesAgendaInterface):
        self.usecase = usecase

    def create_agenda(self, name: str):
        return self.usecase.create_agendamento(name)
    
   

