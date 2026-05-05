
from ..Modules.User.Aplication.UseCases import createUseCase, deleteUseCase, detailUseCase, listUseCase, updateUseCase
from ..Infra .RepoAdapter.UserRepository import UserRepository

#uma formM
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

#forma 2
'''
def router_factory():
    repository = AgendaRepository()
    usecase = UseCasesAgenda(repository)
    controller = AgendaController(usecase)
    return AgendaRouter(controller).router

'''

#atual
class UserFactory:
    def useCaseCreateUser_factory():
        repository = UserRepository()
        usecase = createUseCase.CreateUserUseCase(repository)
        return usecase
    

    def useCaseDeleteUser_factory():
        repository = UserRepository()
        usecase = deleteUseCase.DeleteUserUseCase(repository)
        return usecase


    def useCaseUpdateUser_factory():
        repository = UserRepository()
        usecase = updateUseCase.UpdateUserUseCase(repository)
        return usecase


    def useCaseListUser_factory():
        repository = UserRepository()
        usecase = listUseCase.ListUserUseCase(repository)
        return usecase


    def useCaseDetailUser_factory():
        repository = UserRepository()
        usecase = detailUseCase.DetailUserUseCase(repository)
        return usecase



