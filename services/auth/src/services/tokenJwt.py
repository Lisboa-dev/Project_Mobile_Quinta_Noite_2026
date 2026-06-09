import base64
import hmac
import json
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Optional

try:
    from authlib.jose import JoseError, jwt
except ImportError:  # pragma: no cover - exercised only in minimal test environments
    JoseError = Exception
    jwt = None

from ..config import get_settings


class TokenService:
    @staticmethod
    def _encode(payload: dict) -> str:
        settings = get_settings()
        if jwt is None:
            return TokenService._encode_fallback(payload)
        token = jwt.encode({"alg": settings.JWT_ALGORITHM}, payload, settings.JWT_SECRET)
        return token.decode("utf-8") if isinstance(token, bytes) else token

    @staticmethod
    def _base64url_encode(payload: bytes) -> str:
        return base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")

    @staticmethod
    def _base64url_decode(payload: str) -> bytes:
        padding = "=" * (-len(payload) % 4)
        return base64.urlsafe_b64decode(f"{payload}{padding}")

    @staticmethod
    def _encode_fallback(payload: dict) -> str:
        settings = get_settings()
        if settings.JWT_ALGORITHM != "HS256":
            raise ValueError("Fallback token encoder only supports HS256")

        header = {"alg": "HS256", "typ": "JWT"}
        encoded_header = TokenService._base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        encoded_payload = TokenService._base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        signature = hmac.new(settings.JWT_SECRET.encode("utf-8"), signing_input, sha256).digest()
        return f"{encoded_header}.{encoded_payload}.{TokenService._base64url_encode(signature)}"

    @staticmethod
    def _decode_fallback(token: str) -> Optional[dict]:
        settings = get_settings()
        try:
            encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
            signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
            expected = hmac.new(settings.JWT_SECRET.encode("utf-8"), signing_input, sha256).digest()
            received = TokenService._base64url_decode(encoded_signature)
            if not hmac.compare_digest(expected, received):
                return None

            payload = json.loads(TokenService._base64url_decode(encoded_payload))
            expires_at = payload.get("exp")
            if expires_at is not None and int(expires_at) < int(datetime.now(timezone.utc).timestamp()):
                return None
            return payload
        except Exception:
            return None

    @staticmethod
    def generate_token(user_id: str, role: str = "user") -> dict:
        settings = get_settings()
        now = datetime.now(timezone.utc)

        access_payload = {
            "sub": str(user_id),
            "role": role,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)).timestamp()),
        }

        refresh_payload = {
            "sub": str(user_id),
            "role": role,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        }

        return {
            "access_token": TokenService._encode(access_payload),
            "refresh_token": TokenService._encode(refresh_payload),
            "token_type": "Bearer",
        }

    @staticmethod
    def validate_token(token: str, refresh_token: str = "") -> bool:
        payload = TokenService.decode_token(token)
        if not payload:
            return False
        return payload.get("type") == "access" or bool(refresh_token)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        if jwt is None:
            return TokenService._decode_fallback(token)

        try:
            settings = get_settings()
            claims = jwt.decode(token, settings.JWT_SECRET)
            claims.validate()
            return dict(claims)
        except JoseError:
            return None

    @staticmethod
    def encode_token(payload: dict) -> str:
        return TokenService._encode(payload)

    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        settings = get_settings()
        payload = TokenService.decode_token(token)

        if not payload or payload.get("type") != "refresh":
            return None

        now = datetime.now(timezone.utc)
        new_access_payload = {
            "sub": payload.get("sub"),
            "role": payload.get("role", "user"),
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)).timestamp()),
        }

        return TokenService._encode(new_access_payload)
