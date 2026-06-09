from __future__ import annotations

from dataclasses import dataclass
import re
from time import monotonic
from urllib.parse import urlparse

import httpx
from starlette.requests import Request

from ..config import get_settings
from .event_log import log_event


READ_METHODS = {"GET", "HEAD", "OPTIONS"}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
SERVICE_PREFIXES = {
    "/agenda": "agenda",
    "/users": "users",
    "/notification": "notification",
    "/analytics": "analytics",
}
ROLE_ALIASES = {
    "admin": "admin",
    "administrator": "admin",
    "atendente": "atendent",
    "atendent": "atendent",
    "attendant": "attendant",
    "medico": "medic",
    "médico": "medic",
    "mÃ©dico": "medic",
    "medic": "medic",
    "doctor": "doctor",
    "paciente": "pacient",
    "pacient": "pacient",
    "patient": "patient",
    "user": "user",
}


ROUTE_POLICIES: tuple[tuple[set[str], re.Pattern[str], str], ...] = (
    ({"POST"}, re.compile(r"^/users/admins/doctors/?$"), "users.doctors.create"),
    ({"POST"}, re.compile(r"^/users/medics/?$"), "users.doctors.create"),
    (WRITE_METHODS, re.compile(r"^/users/admins(/.*)?$"), "users.admins.manage"),
    (WRITE_METHODS, re.compile(r"^/users/(users|atendents|attendants|pacients|patients|medics|doctors)(/.*)?$"), "users.users.manage"),
    ({"POST"}, re.compile(r"^/agenda/(appointments|appointment)(/.*)?$"), "agenda.appointments.create"),
    ({"PUT", "PATCH", "DELETE"}, re.compile(r"^/agenda/(appointments|appointment)(/.*)?$"), "agenda.appointments.manage"),
    (WRITE_METHODS, re.compile(r"^/agenda/(calendars|calendar|clinics|clinic|doctors|doctor|patients|patient|rooms|room|rules|rule)(/.*)?$"), "agenda.resources.manage"),
    (READ_METHODS, re.compile(r"^/notification/notifications/(patients|pacients)(/.*)?$"), "notifications.patient.read"),
    (READ_METHODS, re.compile(r"^/notification/notifications/(medics|doctors)(/.*)?$"), "notifications.doctor.read"),
    (READ_METHODS, re.compile(r"^/notification/notifications/admins(/.*)?$"), "notifications.admin.read"),
    (WRITE_METHODS, re.compile(r"^/notification/notifications(/.*)?$"), "notifications.manage"),
    (READ_METHODS, re.compile(r"^/analytics/operations(/.*)?$"), "analytics.operations.read"),
    (READ_METHODS, re.compile(r"^/analytics/doctors(/.*)?$"), "analytics.doctors.read"),
)


@dataclass
class AuthorizationDecision:
    allowed: bool
    reason: str | None = None


class OpenFGAAuthorizationService:
    _store_id: str | None = None
    _store_loaded_at: float = 0.0
    _store_ttl_seconds: float = 60.0

    async def authorize(self, request: Request, payload: dict) -> AuthorizationDecision:
        settings = get_settings()
        if not settings.OPENFGA_ENABLED:
            return AuthorizationDecision(True, "openfga_disabled")

        user_id = str(payload.get("sub", "")).strip()
        role = self._normalize_role(str(payload.get("role", "user")))
        path = self._forwarded_path(request)
        service = self._service_from_path(path)
        method = self._forwarded_method(request)
        relation = self._relation_from_method(method)
        route_permission = self._route_permission(path, method)

        if not user_id:
            return AuthorizationDecision(False, "missing_user")
        if service is None:
            return AuthorizationDecision(True, "public_or_unmapped_path")

        try:
            if route_permission:
                allowed = await self._check_route_permission(
                    user_id=user_id,
                    role=role,
                    permission=route_permission,
                )
            else:
                allowed = await self._check(user_id=user_id, role=role, service=service, relation=relation)
        except httpx.HTTPError as exc:
            if settings.OPENFGA_AUTHZ_FAIL_OPEN:
                return AuthorizationDecision(True, f"openfga_error_fail_open:{exc.__class__.__name__}")
            return AuthorizationDecision(False, f"openfga_error:{exc.__class__.__name__}")

        log_event(
            "AuthorizationChecked",
            "auth.authorization.checked",
            {
                "user_id": user_id,
                "role": role,
                "service": service,
                "relation": relation,
                "route_permission": route_permission,
                "allowed": allowed,
            },
        )
        return AuthorizationDecision(allowed, None if allowed else "forbidden")

    def _normalize_role(self, role: str) -> str:
        normalized = role.strip().lower()
        return ROLE_ALIASES.get(normalized, normalized or "user")

    def _forwarded_path(self, request: Request) -> str:
        forwarded_uri = request.headers.get("x-forwarded-uri")
        if forwarded_uri:
            parsed = urlparse(forwarded_uri)
            return parsed.path or "/"
        return request.url.path

    def _forwarded_method(self, request: Request) -> str:
        return request.headers.get("x-forwarded-method", request.method).upper()

    def _service_from_path(self, path: str) -> str | None:
        normalized = path if path.startswith("/") else f"/{path}"
        for prefix, service in SERVICE_PREFIXES.items():
            if normalized == prefix or normalized.startswith(f"{prefix}/"):
                return service
        return None

    def _relation_from_method(self, method: str) -> str:
        if method in READ_METHODS:
            return "can_read"
        if method in WRITE_METHODS:
            return "can_write"
        return "can_admin"

    def _route_permission(self, path: str, method: str) -> str | None:
        normalized = path if path.startswith("/") else f"/{path}"
        normalized = normalized.rstrip("/") or "/"
        for methods, pattern, permission in ROUTE_POLICIES:
            if method in methods and pattern.match(normalized):
                return permission
        return None

    async def _store(self, client: httpx.AsyncClient) -> str:
        now = monotonic()
        if self._store_id and now - self._store_loaded_at < self._store_ttl_seconds:
            return self._store_id

        settings = get_settings()
        response = await client.get("/stores")
        response.raise_for_status()
        stores = response.json().get("stores", [])
        for store in stores:
            if store.get("name") == settings.OPENFGA_STORE_NAME:
                self._store_id = str(store["id"])
                self._store_loaded_at = now
                return self._store_id

        raise httpx.HTTPStatusError(
            "OpenFGA store not found",
            request=response.request,
            response=response,
        )

    async def _check(self, user_id: str, role: str, service: str, relation: str) -> bool:
        settings = get_settings()
        async with httpx.AsyncClient(
            base_url=settings.OPENFGA_API_URL.rstrip("/"),
            timeout=settings.HTTP_TIMEOUT,
        ) as client:
            store_id = await self._store(client)
            response = await client.post(
                f"/stores/{store_id}/check",
                json={
                    "tuple_key": {
                        "user": f"user:{user_id}",
                        "relation": relation,
                        "object": f"service:{service}",
                    },
                    "contextual_tuples": {
                        "tuple_keys": [
                            {
                                "user": f"user:{user_id}",
                                "relation": "member",
                                "object": f"role:{role}",
                            }
                        ]
                    },
                },
            )
            response.raise_for_status()
            return bool(response.json().get("allowed", False))

    async def _check_route_permission(self, user_id: str, role: str, permission: str) -> bool:
        settings = get_settings()
        async with httpx.AsyncClient(
            base_url=settings.OPENFGA_API_URL.rstrip("/"),
            timeout=settings.HTTP_TIMEOUT,
        ) as client:
            store_id = await self._store(client)
            response = await client.post(
                f"/stores/{store_id}/check",
                json={
                    "tuple_key": {
                        "user": f"user:{user_id}",
                        "relation": "can_access",
                        "object": f"route_permission:{permission}",
                    },
                    "contextual_tuples": {
                        "tuple_keys": [
                            {
                                "user": f"user:{user_id}",
                                "relation": "member",
                                "object": f"role:{role}",
                            }
                        ]
                    },
                },
            )
            response.raise_for_status()
            return bool(response.json().get("allowed", False))


authorization_service = OpenFGAAuthorizationService()
