
from services.notificacaoService.src.API.Controllers.AgendaController import AgendaController
from services.notificacaoService.src.API.router import AgendaRouter
from Aplication.UseCases.exampleHandler import UseCasesAgenda
from services.notificacaoService.src.Infra.Repositorys.AgendaRepository import AgendaRepository


'''
def get_repository_factory():
    # Aqui você pode criar e configurar a instância do seu repositório
    # Por exemplo, se você tiver uma implementação concreta do repositório:
    from ...Infrastructure.Repositories import AgendaRepository
    return AgendaRepository()


def get_usecase_factory():
    # Aqui você pode criar e configurar a instância do seu use case
    # Por exemplo, se você tiver uma implementação concreta do UseCasesAgendaInterface:
    from ...Aplication.UseCases import UseCasesAgenda
    return UseCasesAgenda(get_repository_factory())


def get_controller_factory():
    return AgendaController(get_usecase_factory())

'''
def router_factory():
    repository = AgendaRepository()
    usecase = UseCasesAgenda(repository)
    controller = AgendaController(usecase)
    return AgendaRouter(controller).router