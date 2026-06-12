from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status

from src.api.ApiSchemas import ClientConfigResponse, ErrorResponse, UserCreateRequest, UserResponse, UserUpdateRequest
from src.api.ControllerUtils import dto_to_response, handle_domain_exception
from src.api.provider import UserFactory
from src.infra.config.settings import (
    MINIO_BUCKET_NAME,
    MINIO_PUBLIC_URL,
    PROFILE_IMAGE_ALLOWED_TYPES,
    PROFILE_IMAGE_MAX_BYTES,
)
from src.infra.externServices.MinioProfileImageStorage import MinioProfileImageStorage
from src.api.validate import validate_profile_image_content_type, validate_profile_image_size
from src.modules.users.application.dtos.useCase.command import AddImageCommand
from src.modules.users.application.dtos.useCase.output import UserOutputDTO
from src.modules.users.domain.entities.UserEntity import User
from src.modules.users.domain.exceptions.DomainExceptions import UserAlreadyExistsException, UserNotFoundException


routerUsersCrud = APIRouter(prefix="/users", tags=["users"])
routerClientConfig = APIRouter(prefix="/config", tags=["config"])


def profile_image_storage_factory() -> MinioProfileImageStorage:
    return MinioProfileImageStorage()


@routerClientConfig.get("/client", response_model=ClientConfigResponse)
def client_config():
    return {
        "profileImage": {
            "maxBytes": PROFILE_IMAGE_MAX_BYTES,
            "allowedTypes": sorted(PROFILE_IMAGE_ALLOWED_TYPES),
            "bucket": MINIO_BUCKET_NAME,
            "publicUrl": MINIO_PUBLIC_URL,
        }
    }


@routerUsersCrud.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, responses={409: {"model": ErrorResponse}})
def create_user(data: UserCreateRequest, repository=Depends(UserFactory.user_repository_factory)):
    try:
        user = User(
            userName=data.userName,
            email=data.email,
            nome=data.name,
            password=data.password,
            cargo=data.cargo,
        )
        if repository.find_by_username(user.userName.value):
            raise UserAlreadyExistsException("userName")
        if repository.find_by_email(user.email.value):
            raise UserAlreadyExistsException("email")
        return dto_to_response(UserOutputDTO.from_entity(repository.save(user)))
    except Exception as exc:
        handle_domain_exception(exc)


@routerUsersCrud.get("/", response_model=list[UserResponse])
def list_users(repository=Depends(UserFactory.user_repository_factory)):
    return [dto_to_response(UserOutputDTO.from_entity(user)) for user in repository.find_all()]


@routerUsersCrud.get("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def detail_user(user_id: str, repository=Depends(UserFactory.user_repository_factory)):
    try:
        user = repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return dto_to_response(UserOutputDTO.from_entity(user))
    except Exception as exc:
        handle_domain_exception(exc)


@routerUsersCrud.put("/{user_id}", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def update_user(user_id: str, data: UserUpdateRequest, repository=Depends(UserFactory.user_repository_factory)):
    try:
        payload = data.model_dump(exclude_unset=True)
        updated = repository.update(user_id, payload)
        if updated is None:
            raise UserNotFoundException(user_id)
        return dto_to_response(UserOutputDTO.from_entity(updated))
    except Exception as exc:
        handle_domain_exception(exc)


@routerUsersCrud.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}})
def delete_user(
    user_id: str,
    repository=Depends(UserFactory.user_repository_factory),
    storage: MinioProfileImageStorage = Depends(profile_image_storage_factory),
):
    try:
        user = repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        storage.delete(user.profile_image_object)
        repository.delete(user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as exc:
        handle_domain_exception(exc)


@routerUsersCrud.post("/{user_id}/profile-image", response_model=UserResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def upload_profile_image(
    user_id: str,
    file: UploadFile = File(...),
    use_case=Depends(UserFactory.add_profile_image_use_case),
    storage: MinioProfileImageStorage = Depends(profile_image_storage_factory),
):
    stored = None
    try:
        content_type = file.content_type or "application/octet-stream"
        validate_profile_image_content_type(content_type)
        content = await file.read(PROFILE_IMAGE_MAX_BYTES + 1)
        validate_profile_image_size(content)
        stored = storage.save(user_id, file.filename or "profile-image", content_type, content)
        result = await use_case.execute(
            AddImageCommand(
                user_id=user_id,
                image_url=stored.url,
                image_object=stored.object_name,
            )
        )
        previous_object = result.data.get("previous_profile_image_object")
        storage.delete(previous_object)
        return dto_to_response(result)
    except HTTPException:
        raise
    except Exception as exc:
        if stored is not None:
            storage.delete(stored.object_name)
        handle_domain_exception(exc)


@routerUsersCrud.delete("/{user_id}/profile-image", response_model=UserResponse, responses={404: {"model": ErrorResponse}})
def delete_profile_image(
    user_id: str,
    repository=Depends(UserFactory.user_repository_factory),
    storage: MinioProfileImageStorage = Depends(profile_image_storage_factory),
):
    try:
        user = repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        storage.delete(user.profile_image_object)
        updated = repository.update(
            user_id,
            {
                "profile_image_url": None,
                "profile_image_object": None,
            },
        )
        if updated is None:
            raise UserNotFoundException(user_id)
        return dto_to_response(UserOutputDTO.from_entity(updated))
    except Exception as exc:
        handle_domain_exception(exc)
