


#exemplo controler sem factory, com lambda para injetar dependência
#lambda omite a função de factory
'''
@router.post("/")
def create_user(
    name: str,
    controller: AgendaController = Depends(
        lambda: UserController(UseCasesAgendaInterface())
    )
):
    return controller.create_agendamento(name)
'''


#com class

'''

    from fastapi import APIRouter, Depends

class AgendaRouter:
    def __init__(self, controller: AgendaController = Depends(lambda: AgendaController(UseCasesAgendaImpl()))):
        self.controller = controller
        self.router = APIRouter(prefix="/agenda")
        self._setup_routes()

    def _setup_routes(self):
        # rota vinculada ao método da classe
        self.router.post("/")(self.create_agenda)

    async def create_agenda(self, name: str):
        # aqui já usamos o controller injetado
        return self.controller.create_agenda(name)
'''



#com função usando depends
'''
router = APIRouter(prefix="/agenda")

@router.post("/")
def create_agenda(
    name: str,
    controller: AgendaController = Depends(get_controller_factory)
):
    return controller.create_agenda(name)

'''

#com class usando depends
'''

from fastapi import APIRouter, Depends

class AgendaRouter:
    def __init__(self, controller: AgendaController):
        self.controller = controller
       

    # rota como método de classe
    async def create_agenda(self, name: str):
        return self.controller.create_agenda(name)
    

'''



#class AgendaRouter resumida
'''
class AgendaRouter:
    def __init__(self, controller: AgendaController):
        self.controller = controller
        self.router = APIRouter(prefix="/agenda")
        self._setup_routes()

    def _setup_routes(self):
        # rota vinculada ao método da classe
        self.router.post("/")(self.controller.create_agenda)
'''





