from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Usuario
from src.modules.users.domain.entities.MedicEntity import Medic
from src.modules.users.domain.entities.UserEntity import User


class UserMapper:
    @staticmethod
    def to_domain(model: Usuario | None) -> User | None:
        if model is None:
            return None
        cargo = model.cargo.value if hasattr(model.cargo, "value") else model.cargo
        common = {
            "id": str(model.id),
            "userName": model.userName,
            "name": model.nome,
            "email": model.email,
            "password": model.senha,
            "profile_image_url": model.profile_image_url,
            "profile_image_object": model.profile_image_object,
            "password_hashed": True,
        }
        if cargo == CargoEnum.MEDICO.value:
            return Medic(
                **common,
                crm=model.doctor.crm if model.doctor is not None else None,
            )
        return User(**common, cargo=cargo)

    @staticmethod
    def to_persistence_dict(user: User) -> dict:
        data = user.to_dict()
        return {
            "userName": data["userName"],
            "nome": data["nome"],
            "email": data["email"],
            "senha": data.get("senha") or "",
            "cargo": data.get("cargo") or "PACIENTE",
            "profile_image_url": data.get("profile_image_url"),
            "profile_image_object": data.get("profile_image_object"),
            "crm": getattr(user, "crm", None),
        }
