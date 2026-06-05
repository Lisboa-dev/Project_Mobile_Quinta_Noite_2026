from src.infra.config.db.liteSql.LiteSql import get_query
from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Usuario
from src.modules.users.domain.entities.UserEntity import User

from .UserRepositorySqlAlchemy import UserRepository


class RoleScopedUserRepository(UserRepository):
    def __init__(self, cargo: str):
        self.cargo = CargoEnum(cargo)

    def _matches_scope(self, user: User | None) -> bool:
        return bool(user and user.cargo.valor == self.cargo.value)

    def save(self, user: User) -> User:
        user.cargo.value = self.cargo
        return super().save(user)

    def find_all(self) -> list[User]:
        with get_query() as session:
            models = session.query(Usuario).filter(Usuario.cargo == self.cargo).all()
            return [self._to_domain(model) for model in models]

    def find_by_id(self, id: int) -> User | None:
        user = super().find_by_id(id)
        return user if self._matches_scope(user) else None

    def find_by_email(self, email: str) -> User | None:
        user = super().find_by_email(email)
        return user if self._matches_scope(user) else None

    def find_by_username(self, username: str) -> User | None:
        user = super().find_by_username(username)
        return user if self._matches_scope(user) else None
