from fastapi import APIRouter, Depends, Response, status

from src.api.ApiSchemas import ErrorResponse, UserCreateRequest, UserResponse, UserUpdateRequest
from src.api.ControllerUtils import dto_to_response, handle_domain_exception
from src.api.Provider import UserFactory


routerMedics = APIRouter(prefix="/medics", tags=["medics"])
routerUsers = routerMedics


@routerMedics.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
def create_medic(data: UserCreateRequest, use_case=Depends(UserFactory.create_medic_use_case)):
    try:
        return dto_to_response(use_case.execute(data))
    except Exception as exc:
        handle_domain_exception(exc)


@routerMedics.get("/", response_model=list[UserResponse])
def list_medics(use_case=Depends(UserFactory.list_medic_use_case)):
    return [dto_to_response(item) for item in use_case.execute()]


@routerMedics.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def detail_medic(user_id: int, use_case=Depends(UserFactory.detail_medic_use_case)):
    try:
        return dto_to_response(use_case.execute(user_id))
    except Exception as exc:
        handle_domain_exception(exc)


@routerMedics.put("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def update_medic(user_id: int, data: UserUpdateRequest, use_case=Depends(UserFactory.update_medic_use_case)):
    try:
        payload = data.model_dump(exclude_unset=True)
        payload["id"] = user_id
        return dto_to_response(use_case.execute(payload))
    except Exception as exc:
        handle_domain_exception(exc)


@routerMedics.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}})
def delete_medic(user_id: int, use_case=Depends(UserFactory.delete_medic_use_case)):
    try:
        use_case.execute(user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        handle_domain_exception(exc)
