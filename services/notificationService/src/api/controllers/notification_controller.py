from fastapi import APIRouter, HTTPException, Query, Request, status

from src.services import NotificationQueryService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_service(request: Request) -> NotificationQueryService:
    return request.app.state.notification_query_service


@router.get("/users/{user_id}")
def list_user_notifications(
    user_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return get_service(request).list_by_user(user_id=user_id, limit=limit, unread_only=unread_only)


@router.get("/users/{user_id}/bell")
def get_user_bell(user_id: str, request: Request) -> dict:
    return get_service(request).bell(user_id)


@router.get("/users/{user_id}/unread-count")
def count_unread_user_notifications(user_id: str, request: Request) -> dict[str, int | str]:
    return {"user_id": user_id, "unread": get_service(request).count_unread(user_id)}


@router.get("/patients/{patient_id}/bell")
def get_patient_bell(patient_id: str, request: Request) -> dict:
    return get_service(request).bell(patient_id)


@router.get("/pacients/{patient_id}/bell")
def get_pacient_bell(patient_id: str, request: Request) -> dict:
    return get_patient_bell(patient_id, request)


@router.get("/patients/{patient_id}")
def list_patient_notifications(
    patient_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return get_service(request).list_by_user(user_id=patient_id, limit=limit, unread_only=unread_only)


@router.get("/pacients/{patient_id}")
def list_pacient_notifications(
    patient_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return list_patient_notifications(patient_id, request, limit, unread_only)


@router.get("/medics/{doctor_id}/bell")
def get_medic_bell(doctor_id: str, request: Request) -> dict:
    return get_service(request).bell(doctor_id)


@router.get("/doctors/{doctor_id}/bell")
def get_doctor_bell(doctor_id: str, request: Request) -> dict:
    return get_medic_bell(doctor_id, request)


@router.get("/medics/{doctor_id}")
def list_medic_notifications(
    doctor_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return get_service(request).list_by_user(user_id=doctor_id, limit=limit, unread_only=unread_only)


@router.get("/doctors/{doctor_id}")
def list_doctor_notifications(
    doctor_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return list_medic_notifications(doctor_id, request, limit, unread_only)


@router.get("/admins/bell")
def get_admin_bell(request: Request) -> dict:
    return get_service(request).bell("admin")


@router.get("/admins")
def list_admin_notifications(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return get_service(request).list_by_user(user_id="admin", limit=limit, unread_only=unread_only)


@router.get("/admins/{admin_id}/bell")
def get_admin_bell_by_id(admin_id: str, request: Request) -> dict:
    bell = get_service(request).bell("admin")
    return {**bell, "admin_id": admin_id}


@router.get("/admins/{admin_id}")
def list_admin_notifications_by_id(
    admin_id: str,
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    unread_only: bool = Query(default=False),
) -> list[dict]:
    return list_admin_notifications(request, limit, unread_only)


@router.get("/{notification_id}")
def detail_notification(notification_id: str, request: Request) -> dict:
    notification = get_service(request).detail(notification_id)
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.patch("/{notification_id}/read")
def mark_notification_read(notification_id: str, request: Request) -> dict:
    notification = get_service(request).mark_read(notification_id)
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification
