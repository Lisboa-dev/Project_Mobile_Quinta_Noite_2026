from src.infra.config.db.liteSql.LiteSql import get_query
from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Usuario
from src.modules.users.domain.entities.UserEntity import User
from sqlalchemy.orm import joinedload

from .UserRepositorySqlAlchemy import UserRepository


class RoleScopedUserRepository(UserRepository):
    def __init__(self, cargo: str):
        self.cargo = CargoEnum(cargo)

    def _matches_scope(self, user: User | None) -> bool:
        cargo = getattr(user, "cargo", None)
        if isinstance(cargo, tuple) and len(cargo) == 1:
            cargo = cargo[0]
        cargo_value = getattr(cargo, "valor", None) or getattr(cargo, "value", cargo)
        return bool(user and cargo_value == self.cargo.value)

    def save(self, user: User) -> User:
        user.cargo = type(user.cargo)(self.cargo.value)
        return super().save(user)

    def find_all(self) -> list[User]:
        with get_query() as session:
            models = (
                session.query(Usuario)
                .options(joinedload(Usuario.doctor))
                .filter(Usuario.cargo == self.cargo)
                .order_by(Usuario.id.asc())
                .all()
            )
            return [user for user in (self._to_domain(model) for model in models) if user is not None]

    def find_by_id(self, id: str) -> User | None:
        user = super().find_by_id(id)
        return user if self._matches_scope(user) else None

    def find_by_email(self, email: str) -> User | None:
        user = super().find_by_email(email)
        return user if self._matches_scope(user) else None

    def find_by_username(self, username: str) -> User | None:
        user = super().find_by_username(username)
        return user if self._matches_scope(user) else None
