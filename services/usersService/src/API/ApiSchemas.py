from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_CARGOS = {"ADMIN", "MEDICO", "ATENDENTE", "PACIENTE", "GERENTE", "SUPERVISOR"}


class UserCreateRequest(BaseModel):
    userName: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=255)
    name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    cargo: str = "PACIENTE"

    @field_validator("cargo")
    @classmethod
    def validate_cargo(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_CARGOS:
            raise ValueError(f"cargo deve ser um de: {', '.join(sorted(VALID_CARGOS))}")
        return normalized


class MedicCreateRequest(BaseModel):
    userName: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=255)
    name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    crm: str = Field(min_length=3, max_length=64)


class AtendenteCreateRequest(BaseModel):
    userName: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=255)
    name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    cpf: str = Field(min_length=11, max_length=14)


class PacientCreateRequest(BaseModel):
    userName: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=255)
    name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)
    cpf: str = Field(min_length=11, max_length=14)


class UserUpdateRequest(BaseModel):
    userName: str | None = Field(default=None, min_length=3, max_length=80)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    name: str | None = Field(default=None, min_length=2, max_length=160)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    cargo: str | None = None
    crm: str | None = Field(default=None, min_length=3, max_length=64)
    cpf: str | None = Field(default=None, min_length=11, max_length=14)

    @field_validator("cargo")
    @classmethod
    def validate_optional_cargo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if normalized not in VALID_CARGOS:
            raise ValueError(f"cargo deve ser um de: {', '.join(sorted(VALID_CARGOS))}")
        return normalized


class UserResponse(BaseModel):
    id: str | None
    userName: str
    email: str
    name: str
    cargo: str | None
    profileImageUrl: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UseCaseResponse(BaseModel):
    success: bool
    use_case: str
    action: str
    resource: str
    resource_id: str | None = None
    triggered_by_id: str | None = None
    event_name: str | None = None
    message: str | None = None
    data: dict = Field(default_factory=dict)


class ProfileImageClientConfig(BaseModel):
    maxBytes: int
    allowedTypes: list[str]
    bucket: str
    publicUrl: str


class ClientConfigResponse(BaseModel):
    profileImage: ProfileImageClientConfig


class ErrorResponse(BaseModel):
    detail: str
