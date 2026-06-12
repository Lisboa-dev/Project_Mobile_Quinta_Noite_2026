from typing import overload
from uuid import uuid4

from src.infra.config.db.liteSql.LiteSql import get_query
from src.infra.mapper.domain.UserMapper import UserMapper
from sqlalchemy.orm import joinedload

from src.infra.models.sqlAlchemy.UserSqlSchamy import CargoEnum, Doctor, Usuario
from src.modules.users.domain.entities.UserEntity import User
from src.modules.users.domain.valueObjects.PasswordVO import Password


class UserRepository:
    @overload
    def _to_domain(self, model: Usuario) -> User:
        ...

    @overload
    def _to_domain(self, model: None) -> None:
        ...

    def _to_domain(self, model: Usuario | None) -> User | None:
        return UserMapper.to_domain(model)

    def save(self, user: User) -> User:
        data = UserMapper.to_persistence_dict(user)
        user_id = data.get("id") or str(uuid4())
        with get_query() as session:
            model = Usuario(
                id=user_id,
                userName=data["userName"],
                nome=data["nome"],
                email=data["email"],
                senha=data["senha"],
                cargo=CargoEnum(data["cargo"]),
                profile_image_url=data.get("profile_image_url"),
                profile_image_object=data.get("profile_image_object"),
            )
            session.add(model)
            session.flush()
            if model.cargo == CargoEnum.MEDICO and data.get("crm"):
                session.add(Doctor(id=str(uuid4()), user_id=model.id, crm=data["crm"]))
                session.flush()
            session.refresh(model)
            return self._to_domain(model)

    def find_all(self) -> list[User]:
        with get_query() as session:
            return [
                self._to_domain(model)
                for model in session.query(Usuario).options(joinedload(Usuario.doctor)).order_by(Usuario.id.asc()).all()
            ]

    def find_by_id(self, id: str) -> User | None:
        with get_query() as session:
            return self._to_domain(
                session.query(Usuario).options(joinedload(Usuario.doctor)).filter(Usuario.id == id).first()
            )

    def find_by_email(self, email: str) -> User | None:
        with get_query() as session:
            return self._to_domain(
                session.query(Usuario).options(joinedload(Usuario.doctor)).filter(Usuario.email == email).first()
            )

    def find_by_username(self, username: str) -> User | None:
        with get_query() as session:
            return self._to_domain(
                session.query(Usuario).options(joinedload(Usuario.doctor)).filter(Usuario.userName == username).first()
            )

    def update(self, id: str, data: dict) -> User | None:
        with get_query() as session:
            model = session.query(Usuario).filter(Usuario.id == id).first()
            if model is None:
                return None

            field_map = {
                "password": "senha",
                "name": "nome",
                "profileImageUrl": "profile_image_url",
                "profileImageObject": "profile_image_object",
            }
            for key, value in data.items():
                if key == "crm":
                    if model.doctor is None and value:
                        model.doctor = Doctor(id=str(uuid4()), user_id=model.id, crm=value)
                    elif model.doctor is not None and value:
                        model.doctor.crm = value
                    continue
                model_key = field_map.get(key, key)
                if model_key == "senha" and value:
                    value = Password._hash_password(value)
                if model_key == "cargo" and value:
                    value = CargoEnum(value)
                if isinstance(model_key, str) and hasattr(model, model_key):
                    setattr(model, model_key, value)
            session.flush()
            session.refresh(model)
            return self._to_domain(model)

    def delete(self, id: str) -> bool:
        with get_query() as session:
            model = session.query(Usuario).filter(Usuario.id == id).first()
            if model is None:
                return False
            session.delete(model)
            return True

    def add_profile_image(self, id: str, profile_image_url: str, profile_image_object: str) -> None:
        self.update(
            id,
            {
                "profile_image_url": profile_image_url,
                "profile_image_object": profile_image_object,
            },
        )
