from src.infra.adapters.EventBus import InMemoryEventBus
from src.infra.adapters.RoleScopedUserRepository import RoleScopedUserRepository
from src.infra.adapters.UserRepositorySqlAlchemy import UserRepository
from src.modules.users.application.useCases.commands.AddImageUseCase import AddImageUseCase
from src.modules.users.application.useCases.commands.Pacient.CreateUseCase import CreatePacientUseCase
from src.modules.users.application.useCases.commands.Pacient.DeleteUseCase import DeletePacientUseCase
from src.modules.users.application.useCases.commands.admin.depreciatUser import DepreciatUserUseCase
from src.modules.users.application.useCases.commands.admin.promoteUser import PromoteUserUseCase
from src.modules.users.application.useCases.commands.atendent.CreateUseCase import CreateAtendentUseCase
from src.modules.users.application.useCases.commands.atendent.DeleteUseCase import DeleteAtendentUseCase
from src.modules.users.application.useCases.commands.medic.CreateUseCase import CreateMedicUseCase
from src.modules.users.application.useCases.commands.medic.DeleteUseCase import DeleteMedicUseCase
from src.modules.users.application.useCases.querys.admin.DetailUseCase import DetailAdminUseCase
from src.modules.users.application.useCases.querys.admin.ListUseCase import ListAdminUseCase
from src.modules.users.application.useCases.querys.atendent.DetailUseCase import DetailAtendentUseCase
from src.modules.users.application.useCases.querys.atendent.ListUseCase import ListAtendentUseCase
from src.modules.users.application.useCases.querys.medic.DetailUseCase import DetailMedicUseCase
from src.modules.users.application.useCases.querys.medic.ListUseCase import ListMedicUseCase
from src.modules.users.application.useCases.querys.pacient.DetailUseCase import DetailPacientUseCase
from src.modules.users.application.useCases.querys.pacient.ListUseCase import ListPacientUseCase


class UserFactory:
    _event_bus = InMemoryEventBus()

    @staticmethod
    def event_bus_factory():
        return UserFactory._event_bus

    @staticmethod
    def medic_repository_factory() -> RoleScopedUserRepository:
        return RoleScopedUserRepository("MEDICO")

    @staticmethod
    def atendent_repository_factory() -> RoleScopedUserRepository:
        return RoleScopedUserRepository("ATENDENTE")

    @staticmethod
    def admin_repository_factory() -> RoleScopedUserRepository:
        return RoleScopedUserRepository("ADMIN")

    @staticmethod
    def pacient_repository_factory() -> RoleScopedUserRepository:
        return RoleScopedUserRepository("PACIENTE")

    @staticmethod
    def user_repository_factory() -> UserRepository:
        return UserRepository()

    @staticmethod
    def create_medic_use_case():
        return CreateMedicUseCase(UserFactory.medic_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def update_medic_use_case():
        raise NotImplementedError("UpdateMedicUseCase is not available")

    @staticmethod
    def delete_medic_use_case():
        return DeleteMedicUseCase(UserFactory.medic_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def list_medic_use_case():
        return ListMedicUseCase(UserFactory.medic_repository_factory())

    @staticmethod
    def detail_medic_use_case():
        return DetailMedicUseCase(UserFactory.medic_repository_factory())

    @staticmethod
    def create_atendent_use_case():
        return CreateAtendentUseCase(UserFactory.atendent_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def update_atendent_use_case():
        raise NotImplementedError("UpdateAtendentUseCase is not available")

    @staticmethod
    def delete_atendent_use_case():
        return DeleteAtendentUseCase(UserFactory.atendent_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def list_atendent_use_case():
        return ListAtendentUseCase(UserFactory.atendent_repository_factory())

    @staticmethod
    def detail_atendent_use_case():
        return DetailAtendentUseCase(UserFactory.atendent_repository_factory())

    @staticmethod
    def create_admin_use_case():
        return PromoteUserUseCase(UserFactory.user_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def update_admin_use_case():
        raise NotImplementedError("UpdateAdminUseCase is not available")

    @staticmethod
    def delete_admin_use_case():
        return DepreciatUserUseCase(UserFactory.user_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def list_admin_use_case():
        return ListAdminUseCase(UserFactory.admin_repository_factory())

    @staticmethod
    def detail_admin_use_case():
        return DetailAdminUseCase(UserFactory.admin_repository_factory())

    @staticmethod
    def create_pacient_use_case():
        return CreatePacientUseCase(UserFactory.pacient_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def update_pacient_use_case():
        raise NotImplementedError("UpdatePacientUseCase is not available")

    @staticmethod
    def delete_pacient_use_case():
        return DeletePacientUseCase(UserFactory.pacient_repository_factory(), UserFactory.event_bus_factory())

    @staticmethod
    def list_pacient_use_case():
        return ListPacientUseCase(UserFactory.pacient_repository_factory())

    @staticmethod
    def detail_pacient_use_case():
        return DetailPacientUseCase(UserFactory.pacient_repository_factory())

    @staticmethod
    def add_profile_image_use_case():
        return AddImageUseCase(UserFactory.user_repository_factory(), UserFactory.event_bus_factory())

    useCaseCreateUser_factory = create_medic_use_case
    useCaseDeleteUser_factory = delete_medic_use_case
    useCaseUpdateUser_factory = update_medic_use_case
    useCaseListUser_factory = list_medic_use_case
    useCaseDetailUser_factory = detail_medic_use_case


__all__ = ["UserFactory"]
