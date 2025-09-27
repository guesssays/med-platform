from fastapi import APIRouter, Depends
from app.core.deps import get_current_user, require_role
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@router.get("/admin/ping")
def admin_ping(user: User = Depends(require_role({"clinic_admin", "superadmin"}))):
    return {"ok": True, "role": user.role}
