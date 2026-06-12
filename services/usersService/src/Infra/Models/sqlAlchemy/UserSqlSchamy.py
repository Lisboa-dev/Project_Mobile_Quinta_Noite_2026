import enum
from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Index, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.clients.postgres import Base


class CargoEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    MEDICO = "MEDICO"
    ATENDENTE = "ATENDENTE"
    GERENTE = "GERENTE"
    SUPERVISOR = "SUPERVISOR"
    PACIENTE = "PACIENTE"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    userName: Mapped[str] = mapped_column(String(80), nullable=False, unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    cargo: Mapped[CargoEnum] = mapped_column(
        SAEnum(CargoEnum, name="users_cargo_enum", native_enum=False),
        nullable=False,
        default=CargoEnum.PACIENTE,
        index=True,
    )
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_image_object: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    doctor: Mapped["Doctor | None"] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )


Index("ix_users_cargo_username", UserModel.cargo, UserModel.userName)


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    crm: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped[UserModel] = relationship(back_populates="doctor")


Usuario = UserModel


class EventLog(Base):
    __tablename__ = "event_logs"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    service_name: Mapped[str] = mapped_column(String(80), nullable=False)
    event_name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    routing_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
