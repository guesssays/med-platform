from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.v1.deps import require_role, get_current_user, _to_role_name
from app.models.user import User, UserRole

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/only")
def admin_only(current_user: User = Depends(require_role({UserRole.ADMIN}))):
    # Если сюда дошли — роль прошла проверку
    return {"message": f"Hello Admin {current_user.email}"}


class WhoAmI(BaseModel):
    email: str
    role: str
    is_active: bool


@router.get("/whoami", response_model=WhoAmI)
def whoami(u: User = Depends(get_current_user)) -> WhoAmI:
    role_name = _to_role_name(getattr(u, "role", None))
    # is_active может отсутствовать — фоллбэк к True
    return WhoAmI(
        email=u.email,
        role=role_name,
        is_active=bool(getattr(u, "is_active", True)),
    )
