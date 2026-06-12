from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UseCaseOutputDTO:
    success: bool
    use_case: str
    action: str
    resource: str
    resource_id: str | None = None
    triggered_by_id: str | None = None
    event_name: str | None = None
    message: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def ok(
        cls,
        use_case: str,
        action: str,
        resource: str,
        resource_id: str | None = None,
        triggered_by_id: str | None = None,
        event_name: str | None = None,
        message: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> "UseCaseOutputDTO":
        return cls(
            success=True,
            use_case=use_case,
            action=action,
            resource=resource,
            resource_id=resource_id,
            triggered_by_id=triggered_by_id,
            event_name=event_name,
            message=message,
            data=data or {},
        )

    @classmethod
    def fail(
        cls,
        use_case: str,
        action: str,
        resource: str,
        resource_id: str | None = None,
        triggered_by_id: str | None = None,
        message: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> "UseCaseOutputDTO":
        return cls(
            success=False,
            use_case=use_case,
            action=action,
            resource=resource,
            resource_id=resource_id,
            triggered_by_id=triggered_by_id,
            message=message,
            data=data or {},
        )

    def __getattr__(self, name: str) -> Any:
        user = self.data.get("user")
        if isinstance(user, dict) and name in user:
            return user[name]
        raise AttributeError(name)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "use_case": self.use_case,
            "action": self.action,
            "resource": self.resource,
            "resource_id": self.resource_id,
            "triggered_by_id": self.triggered_by_id,
            "event_name": self.event_name,
            "message": self.message,
            "data": self.data,
        }
