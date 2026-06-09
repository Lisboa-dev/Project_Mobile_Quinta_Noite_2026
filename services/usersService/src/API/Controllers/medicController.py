from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.api.ApiSchemas import ErrorResponse, MedicCreateRequest, UseCaseResponse, UserResponse, UserUpdateRequest
from src.api.ControllerUtils import dto_to_response, handle_domain_exception
from src.api.provider import UserFactory
from src.modules.users.application.dtos.useCase.command import CreateMedicCommand, DeleteMedicCommand


routerMedics = APIRouter(prefix="/medics", tags=["medics"])
routerUsers = routerMedics


@routerMedics.post("/", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
async def create_medic(data: MedicCreateRequest, use_case=Depends(UserFactory.create_medic_use_case)):
    try:
        command = CreateMedicCommand(**data.model_dump())
        return dto_to_response(await use_case.execute(command))
    except Exception as exc:
        handle_domain_exception(exc)


@routerMedics.get("/", response_model=list[UserResponse])
async def list_medics(use_case=Depends(UserFactory.list_medic_use_case)):
    return [dto_to_response(item) for item in await use_case.execute()]


@routerMedics.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
async def detail_medic(user_id: int, use_case=Depends(UserFactory.detail_medic_use_case)):
    try:
        return dto_to_response(await use_case.execute(user_id))
    except Exception as exc:
        handle_domain_exception(exc)


@routerMedics.put("/{user_id}", response_model=UserResponse, responses={501: {"model": ErrorResponse}})
async def update_medic(user_id: int, data: UserUpdateRequest):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="update de medico ainda nao implementado")


@routerMedics.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}})
async def delete_medic(user_id: int, use_case=Depends(UserFactory.delete_medic_use_case)):
    try:
        await use_case.execute(DeleteMedicCommand(id=user_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        handle_domain_exception(exc)
