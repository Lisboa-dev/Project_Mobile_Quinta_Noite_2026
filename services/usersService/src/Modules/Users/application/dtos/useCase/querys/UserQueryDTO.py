from dataclasses import dataclass


@dataclass(frozen=True)
class GetUserByIdQuery:
    id: int
    triggered_by_id: str | None = None


@dataclass(frozen=True)
class ListUsersQuery:
    limit: int | None = None
    offset: int = 0
    cargo: str | None = None
    triggered_by_id: str | None = None
