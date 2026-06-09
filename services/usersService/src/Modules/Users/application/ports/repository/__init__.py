from .MedicRepositoryPort import IMedicRepository, MedicRepositoryPort
from .UserRepositoryPort import IUserRepository, UserRepositoryPort

IAdminRepository = UserRepositoryPort
IAtendenteRepository = UserRepositoryPort

__all__ = [
    "IAdminRepository",
    "IAtendenteRepository",
    "IMedicRepository",
    "IUserRepository",
    "MedicRepositoryPort",
    "UserRepositoryPort",
]
