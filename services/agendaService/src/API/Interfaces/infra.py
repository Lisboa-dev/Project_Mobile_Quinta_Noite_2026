from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InfraEventRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event")
    @classmethod
    def validate_event(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("event cannot be empty")
        return value

    def to_payload(self) -> dict[str, Any]:
        if hasattr(self, "model_dump"):
            return self.model_dump()
        return self.dict()
