from .AdminController import routerAdmins
from .AtendentController import routerAtendents
from .MedicController import routerMedics, routerUsers
from .PacientController import routerPacients
from .UserController import routerClientConfig, routerUsersCrud

__all__ = [
    "routerAdmins",
    "routerAtendents",
    "routerMedics",
    "routerPacients",
    "routerUsers",
    "routerUsersCrud",
    "routerClientConfig",
]
