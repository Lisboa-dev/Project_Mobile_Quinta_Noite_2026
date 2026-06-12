from dataclasses import dataclass


@dataclass(frozen=True)
class UseCaseExceptionDTO:
    message: str
    code: str = "USE_CASE_ERROR"
