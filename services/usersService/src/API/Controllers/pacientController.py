from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.api.ApiSchemas import ErrorResponse, PacientCreateRequest, UseCaseResponse, UserResponse, UserUpdateRequest
from src.api.ControllerUtils import dto_to_response, handle_domain_exception
from src.api.provider import UserFactory
from src.modules.users.application.dtos.useCase.command import CreatePacientCommand, DeletePacientCommand


routerPacients = APIRouter(prefix="/pacients", tags=["pacients"])


@routerPacients.post("/", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
async def create_pacient(data: PacientCreateRequest, use_case=Depends(UserFactory.create_pacient_use_case)):
    try:
        command = CreatePacientCommand(**data.model_dump())
        return dto_to_response(await use_case.execute(command))
    except Exception as exc:
        handle_domain_exception(exc)


@routerPacients.get("/", response_model=list[UserResponse])
async def list_pacients(use_case=Depends(UserFactory.list_pacient_use_case)):
    return [dto_to_response(item) for item in await use_case.execute()]


@routerPacients.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
async def detail_pacient(user_id: str, use_case=Depends(UserFactory.detail_pacient_use_case)):
    try:
        return dto_to_response(await use_case.execute(user_id))
    except Exception as exc:
        handle_domain_exception(exc)


@routerPacients.put("/{user_id}", response_model=UserResponse, responses={501: {"model": ErrorResponse}})
async def update_pacient(user_id: str, data: UserUpdateRequest):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="update de paciente ainda nao implementado")


@routerPacients.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}})
async def delete_pacient(user_id: str, use_case=Depends(UserFactory.delete_pacient_use_case)):
    try:
        await use_case.execute(DeletePacientCommand(id=user_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        handle_domain_exception(exc)
