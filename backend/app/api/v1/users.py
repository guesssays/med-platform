# app/api/v1/users.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from app.api.v1.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool = True  # если поля нет в модели — отдаём True

    class Config:
        from_attributes = True  # pydantic v2 (для .from_orm в v1: orm_mode=True)

@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut(id=current_user.id, email=current_user.email, is_active=True)
