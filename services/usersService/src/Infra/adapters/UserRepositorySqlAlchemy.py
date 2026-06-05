from src.infra.config.db.liteSql.LiteSql import get_query
from src.infra.mapper.domain.UserMapper import UserMapper
from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Usuario
from src.modules.users.domain.entities.UserEntity import User
from src.modules.users.domain.valueObjects.PasswordVO import Password


class UserRepository:
    def _to_domain(self, model: Usuario | None) -> User | None:
        return UserMapper.to_domain(model)

    def save(self, user: User) -> User:
        data = UserMapper.to_persistence_dict(user)
        with get_query() as session:
            model = Usuario(
                userName=data["userName"],
                nome=data["nome"],
                email=data["email"],
                senha=data["senha"],
                cargo=CargoEnum(data["cargo"]),
            )
            session.add(model)
            session.flush()
            session.refresh(model)
            return self._to_domain(model)

    def find_all(self) -> list[User]:
        with get_query() as session:
            return [self._to_domain(model) for model in session.query(Usuario).all()]

    def find_by_id(self, id: int) -> User | None:
        with get_query() as session:
            return self._to_domain(session.query(Usuario).filter(Usuario.id == id).first())

    def find_by_email(self, email: str) -> User | None:
        with get_query() as session:
            return self._to_domain(session.query(Usuario).filter(Usuario.email == email).first())

    def find_by_username(self, username: str) -> User | None:
        with get_query() as session:
            return self._to_domain(session.query(Usuario).filter(Usuario.userName == username).first())

    def update(self, id: int, data: dict) -> User | None:
        with get_query() as session:
            model = session.query(Usuario).filter(Usuario.id == id).first()
            if model is None:
                return None
            field_map = {"password": "senha", "name": "nome"}
            for key, value in data.items():
                model_key = field_map.get(key, key)
                if model_key == "senha" and value:
                    value = Password(value).hash
                if hasattr(model, model_key):
                    setattr(model, model_key, value)
            session.flush()
            session.refresh(model)
            return self._to_domain(model)

    def delete(self, id: int) -> bool:
        with get_query() as session:
            model = session.query(Usuario).filter(Usuario.id == id).first()
            if model is None:
                return False
            session.delete(model)
            return True
