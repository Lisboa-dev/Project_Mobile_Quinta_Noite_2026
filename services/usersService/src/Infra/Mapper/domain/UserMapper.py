from src.infra.models.sqlAlchemy.UserSqlSchamy import Usuario
from src.modules.users.domain.entities.UserEntity import User


class UserMapper:
    @staticmethod
    def to_domain(model: Usuario | None) -> User | None:
        if model is None:
            return None
        cargo = model.cargo.value if hasattr(model.cargo, "value") else model.cargo
        return User(
            id=model.id,
            userName=model.userName,
            nome=model.nome,
            email=model.email,
            password=model.senha,
            cargo=cargo,
            password_hashed=True,
        )

    @staticmethod
    def to_persistence_dict(user: User) -> dict:
        data = user.to_dict()
        return {
            "userName": data["userName"],
            "nome": data["nome"],
            "email": data["email"],
            "senha": data.get("senha") or "",
            "cargo": data.get("cargo") or "PACIENTE",
        }
