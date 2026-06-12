from typing import Any

from pydantic import field_validator, model_validator

from src.api.interfaces.base import (
    ApiInput,
    required_non_empty,
    validate_iso_date_text,
    validate_range_time,
    validate_weekday,
)
from src.modules.agenda.aplication.dtos.useCase.command.RulesUseCasesDTO import (
    CreateBlockRuleCommand,
    CreateGenericRuleCommand,
    CreateSpecificDayRuleCommand,
    CreateSpecificRuleCommand,
    CreateWeekRuleCommand,
)


class CreateBlockRuleRequest(ApiInput):
    date: Any = None
    weekday: int | None = None
    description: str | None = None
    target: str | None = None
    targetType: Any = None
    nome: str | None = None

    @field_validator("weekday")
    @classmethod
    def validate_weekday_value(cls, value: int | None) -> int | None:
        return validate_weekday(value)

    @field_validator("description", "target", "nome")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return required_non_empty(value, info.field_name)

    @field_validator("date")
    @classmethod
    def validate_optional_date(cls, value: Any) -> Any:
        if value is None or isinstance(value, dict):
            return value
        return validate_iso_date_text(value, "date")

    @model_validator(mode="after")
    def validate_has_scope(self):
        if self.date is None and self.weekday is None and self.target is None and self.targetType is None:
            raise ValueError("block rule must define date, weekday, target or targetType")
        return self

    def to_command(self) -> CreateBlockRuleCommand:
        return CreateBlockRuleCommand(
            triggered_by_id=self.triggered_by_id,
            date=self.date,
            weekday=self.weekday,
            description=self.description,
            target=self.target,
            targetType=self.targetType,
            nome=self.nome,
        )


class CreateGenericRuleRequest(ApiInput):
    ruleEffect: Any
    targetType: Any
    rangeTime: Any
    description: str
    nome: str | None = None

    @field_validator("ruleEffect", "targetType", "description")
    @classmethod
    def validate_required_text(cls, value: Any, info):
        return required_non_empty(value, info.field_name)

    @field_validator("rangeTime")
    @classmethod
    def validate_range(cls, value: Any):
        return validate_range_time(value, "rangeTime")

    def to_command(self) -> CreateGenericRuleCommand:
        return CreateGenericRuleCommand(
            ruleEffect=self.ruleEffect,
            targetType=self.targetType,
            rangeTime=self.rangeTime,
            description=self.description,
            triggered_by_id=self.triggered_by_id,
            nome=self.nome,
        )


class CreateSpecificRuleRequest(ApiInput):
    ruleEffect: Any
    id: str | None = None
    type: Any = None
    target: str | None = None
    rangeTime: Any
    description: str
    targetType: Any = None
    nome: str | None = None

    @field_validator("ruleEffect", "description")
    @classmethod
    def validate_required_text(cls, value: Any, info):
        return required_non_empty(value, info.field_name)

    @field_validator("id", "target", "nome")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return required_non_empty(value, info.field_name)

    @field_validator("type", "targetType")
    @classmethod
    def validate_optional_scope_type(cls, value: Any, info):
        if value is None:
            return None
        return required_non_empty(value, info.field_name)

    @model_validator(mode="after")
    def validate_specific_scope(self):
        self.id = self.id or self.target
        self.type = self.type or self.targetType
        if self.id is None:
            raise ValueError("specific rule must define id")
        if self.type is None:
            raise ValueError("specific rule must define type")
        return self

    @field_validator("rangeTime")
    @classmethod
    def validate_range(cls, value: Any):
        return validate_range_time(value, "rangeTime")

    def to_command(self) -> CreateSpecificRuleCommand:
        return CreateSpecificRuleCommand(
            ruleEffect=self.ruleEffect,
            id=self.id or self.target or "",
            type=self.type or self.targetType,
            rangeTime=self.rangeTime,
            description=self.description,
            triggered_by_id=self.triggered_by_id,
            target=self.target,
            targetType=self.targetType,
            nome=self.nome,
        )


class CreateSpecificDayRuleRequest(ApiInput):
    ruleEffect: Any
    rangeTime: Any
    description: str
    date: Any
    target: str | None = None
    targetType: Any = None
    nome: str | None = None

    @field_validator("ruleEffect", "description")
    @classmethod
    def validate_required_text(cls, value: Any, info):
        return required_non_empty(value, info.field_name)

    @field_validator("rangeTime")
    @classmethod
    def validate_range(cls, value: Any):
        return validate_range_time(value, "rangeTime")

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return value
        return validate_iso_date_text(value, "date")

    def to_command(self) -> CreateSpecificDayRuleCommand:
        return CreateSpecificDayRuleCommand(
            ruleEffect=self.ruleEffect,
            rangeTime=self.rangeTime,
            description=self.description,
            date=self.date,
            triggered_by_id=self.triggered_by_id,
            target=self.target,
            targetType=self.targetType,
            nome=self.nome,
        )


class CreateWeekRuleRequest(ApiInput):
    ruleEffect: Any
    rangeTime: Any
    description: str
    weekday: int
    target: str | None = None
    targetType: Any = None
    nome: str | None = None

    @field_validator("ruleEffect", "description")
    @classmethod
    def validate_required_text(cls, value: Any, info):
        return required_non_empty(value, info.field_name)

    @field_validator("weekday")
    @classmethod
    def validate_weekday_value(cls, value: int) -> int:
        return validate_weekday(value)  # type: ignore[return-value]

    @field_validator("rangeTime")
    @classmethod
    def validate_range(cls, value: Any):
        return validate_range_time(value, "rangeTime")

    def to_command(self) -> CreateWeekRuleCommand:
        return CreateWeekRuleCommand(
            ruleEffect=self.ruleEffect,
            rangeTime=self.rangeTime,
            description=self.description,
            weekday=self.weekday,
            triggered_by_id=self.triggered_by_id,
            target=self.target,
            targetType=self.targetType,
            nome=self.nome,
        )
