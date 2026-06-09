from fastapi import Header, HTTPException, status


def require_admin(x_user_role: str | None = Header(default=None, alias="X-User-Role")) -> None:
    role = (x_user_role or "").strip().lower()
    if role in {"admin", "administrator"}:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin role required",
    )
