from enum import Enum

from ..exceptions.DomainExceptions import InvalidCargoException


class CargoEnum(str, Enum):
    ADMIN = "ADMIN"
    MEDICO = "MEDICO"
    ATENDENTE = "ATENDENTE"
    GERENTE = "GERENTE"
    SUPERVISOR = "SUPERVISOR"
    PACIENTE = "PACIENTE"


class Cargo:
    def __init__(self, value: str | CargoEnum | None):
        if value is None:
            self.value = None
            return
        try:
            self.value = value if isinstance(value, CargoEnum) else CargoEnum(str(value).upper())
        except ValueError as exc:
            raise InvalidCargoException(str(value)) from exc

    @property
    def valor(self) -> str | None:
        return self.value.value if self.value else None

    def __str__(self) -> str:
        return self.valor or ""

    def __repr__(self) -> str:
        return f"Cargo('{self.valor}')"
