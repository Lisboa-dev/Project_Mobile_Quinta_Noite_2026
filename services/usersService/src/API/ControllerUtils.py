from fastapi import HTTPException, status

from src.modules.users.domain.exceptions.DomainExceptions import (
    DomainException,
    UserAlreadyExistsException,
    UserNotFoundException,
)


def dto_to_response(dto):
    data = getattr(dto, "data", None)
    if isinstance(data, dict) and isinstance(data.get("user"), dict):
        return data["user"]
    return dto.to_dict() if hasattr(dto, "to_dict") else dto


def handle_domain_exception(exc: Exception):
    if isinstance(exc, UserAlreadyExistsException):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, UserNotFoundException):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, DomainException):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raise exc
