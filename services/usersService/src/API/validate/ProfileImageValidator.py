from fastapi import HTTPException, status

from src.infra.config.settings import PROFILE_IMAGE_ALLOWED_TYPES, PROFILE_IMAGE_MAX_BYTES


def validate_profile_image_content_type(content_type: str) -> None:
    if content_type not in PROFILE_IMAGE_ALLOWED_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tipo de imagem nao permitido")


def validate_profile_image_size(content: bytes) -> None:
    if len(content) > PROFILE_IMAGE_MAX_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="imagem excede o tamanho maximo")
