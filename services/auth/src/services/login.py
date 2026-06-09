import hashlib
import os

try:
    import httpx
except ImportError:  # pragma: no cover - exercised only in minimal test environments
    httpx = None

from ..config import get_settings
from .event_log import log_event
from .tokenJwt import TokenService


def _bearer_token(token: str) -> str:
    parts = token.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1].strip()
    return token.strip()


async def _fetch_user(email: str = "", name: str = "") -> dict | None:
    if os.getenv("TEST_USE_MOCK_DATA", "true").lower() in {"1", "true", "yes", "on"}:
        return None
    if httpx is None:
        return None

    settings = get_settings()
    params = {}
    if email:
        params["email"] = email
    if name:
        params["name"] = name

    if not params:
        return None

    try:
        async with httpx.AsyncClient(
            base_url=settings.USER_SERVICE_URL,
            timeout=settings.HTTP_TIMEOUT,
        ) as client:
            response = await client.get(settings.USER_LOOKUP_PATH, params=params)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError:
        return None

    if isinstance(data, list):
        return data[0] if data else None
    return data if isinstance(data, dict) else None


def _dev_user(email: str = "", name: str = "") -> dict | None:
    settings = get_settings()
    if email and email != settings.AUTH_DEV_USER_EMAIL:
        return None
    if name and name != settings.AUTH_DEV_USER_NAME:
        return None

    return {
        "id": settings.AUTH_DEV_USER_ID,
        "email": settings.AUTH_DEV_USER_EMAIL,
        "name": settings.AUTH_DEV_USER_NAME,
        "password": settings.AUTH_DEV_USER_PASSWORD,
        "role": settings.AUTH_DEV_USER_ROLE,
    }


async def loginService(body: dict) -> dict | None:
    password = body.get("password", "")
    email = body.get("email", "")
    name = body.get("name", "")

    if not password or (not email and not name):
        raise ValueError("email ou name e password sao obrigatorios")

    user = await _fetch_user(email=email, name=name)
    if not user:
        user = _dev_user(email=email, name=name)

    if not user or not validate_password(password, str(user.get("password", ""))):
        log_event("LoginFailed", "auth.login.failed", {"email": email, "name": name})
        return None

    user_id = str(user.get("id"))
    role = str(user.get("role") or user.get("cargo") or "user")
    result = {"user_id": user_id, "tokens": TokenService.generate_token(user_id, role)}
    log_event("LoginSucceeded", "auth.login.succeeded", {"user_id": user_id, "role": role})
    return result


async def validateLoginService(token: str) -> bool:
    return TokenService.validate_token(_bearer_token(token))


def validate_password(password: str, stored_password: str) -> bool:
    if password == stored_password:
        return True
    return hashlib.sha256(password.encode("utf-8")).hexdigest() == stored_password
