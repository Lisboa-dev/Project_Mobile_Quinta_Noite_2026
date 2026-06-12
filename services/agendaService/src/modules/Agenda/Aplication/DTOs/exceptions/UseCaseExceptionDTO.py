from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UseCaseExceptionDTO:
    code: str
    message: str
    use_case: str
    context: dict[str, Any] = field(default_factory=dict)


class UseCaseException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        use_case: str,
        context: dict[str, Any] | None = None,
        original: Exception | None = None,
    ):
        self.error = UseCaseExceptionDTO(
            code=code,
            message=message,
            use_case=use_case,
            context=context or {},
        )
        self.original = original
        super().__init__(self.error.message)

    def __str__(self) -> str:
        text = f"[{self.error.code}] {self.error.use_case}: {self.error.message}"
        if self.original is not None:
            text = f"{text} (caused by {self.original.__class__.__name__}: {self.original})"
        return text


class AgendaUseCaseException(UseCaseException):
    pass


class CreateUseCaseException(AgendaUseCaseException):
    pass


class UpdateUseCaseException(AgendaUseCaseException):
    pass


class DeleteUseCaseException(AgendaUseCaseException):
    pass


class EntityNotFoundUseCaseException(AgendaUseCaseException):
    pass
