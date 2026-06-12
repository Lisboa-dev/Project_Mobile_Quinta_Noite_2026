from dataclasses import dataclass


@dataclass(frozen=True)
class GetByIdQuery:
    id: str


@dataclass(frozen=True)
class ListQuery:
    limit: int | None = None
    offset: int = 0
    type: str | None = None
    id: str | None = None
    target_id: str | None = None
    ruleEffect: str | None = None


@dataclass(frozen=True)
class ListDaysQuery:
    year: int | None = None
    month: int | None = None
    limit: int | None = None
    offset: int = 0
