from typing import Iterable, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db as get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

# Совместимость со старым кодом, где вызывали get_db_dep
def get_db_dep():
    """Alias для совместимости со старым кодом."""
    yield from get_db()

bearer = HTTPBearer(auto_error=False)


def _to_role_name(val: Union[str, UserRole]) -> str:
    """
    Приводим значение роли к ВЕРХНЕМУ_РЕГИСТРУ имени:
      - UserRole.ADMIN       -> "ADMIN"
      - UserRole.ADMIN.value -> "ADMIN"
      - "admin"/"ADMIN"      -> "ADMIN"
    """
    if isinstance(val, UserRole):
        return val.name.upper()
    name = getattr(val, "name", None)
    if isinstance(name, str):
        return name.upper()
    value = getattr(val, "value", None)
    if isinstance(value, str):
        return value.upper()
    return str(val).upper()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_token(creds.credentials)
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.email == sub).first()
    # is_active может не существовать в старой схеме — тогда считаем True
    is_active = bool(getattr(user, "is_active", True)) if user else False
    if not user or not is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")

    return user


def require_role(allowed: Iterable[Union[str, UserRole]]):
    """
    RBAC-зависимость.
      Depends(require_role({UserRole.ADMIN}))  или  Depends(require_role({"ADMIN"}))
    """
    allowed_norm = {_to_role_name(r) for r in allowed}

    def _checker(user: User = Depends(get_current_user)) -> User:
        user_role_norm = _to_role_name(getattr(user, "role", ""))
        if allowed_norm and user_role_norm not in allowed_norm:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _checker
