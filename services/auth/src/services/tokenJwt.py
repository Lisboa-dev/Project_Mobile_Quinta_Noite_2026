
from datetime import datetime, timedelta, timezone
import os
from typing import Optional
from authlib.jose import jwt


class TokenService:
    SECRET_KEY =  os.getenv("JWT_SECRET")
    ALGORITHM = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("TOKEN_EXPIRE_MINUTES") 
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("TOKEN_EXPIRE_MINUTES") 

    @staticmethod
    def generate_token(user_id: int) -> dict:
        now = datetime.now(timezone.utc)

        access_payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES),
        }

        refresh_payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=TokenService.REFRESH_TOKEN_EXPIRE_DAYS),
        }

        access_token = jwt.encode(
            access_payload, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM
        )

        refresh_token = jwt.encode(
            refresh_payload, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    def validate_token(token: str, refresh_token:str = '') -> bool:
        try:
            jwt.decode(token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM]
            )
            return payload
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def encode_token(payload: dict) -> str:
        return jwt.encode(
            payload, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM
        )

    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        payload = TokenService.decode_token(token)

        if not payload or payload.get("type") != "refresh":
            return None

        user_id = payload.get("sub")

        new_access_payload = {
            "sub": user_id,
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES),
        }

        return jwt.encode(
            new_access_payload,
            TokenService.SECRET_KEY,
            algorithm=TokenService.ALGORITHM,
        )