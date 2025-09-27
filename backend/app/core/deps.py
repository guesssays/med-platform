# app/api/v1/deps.py
from typing import Iterable, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import decode_token
from app.models.user import User

# При ошибке авторизации не роняем роутер — сами вернём 401
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """Достаём пользователя из Bearer JWT."""
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = creds.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.email == sub).first()
    if not user or not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or missing user",
        )
    return user


# --- RBAC helpers -----------------------------------------------------------

def _role_to_str(role) -> str:
    """
    Превращает Enum/UserRole.ADMIN -> 'ADMIN',
    'admin' -> 'ADMIN', 'UserRole.ADMIN' -> 'ADMIN'
    """
    # Enum c .name
    name = getattr(role, "name", None)
    if name:
        return str(name).upper()

    s = str(role)
    if "." in s:  # 'UserRole.ADMIN' -> 'ADMIN'
        s = s.split(".")[-1]
    return s.upper()


def require_role(required: Iterable[str] | Set[str]):
    """
    Пример: @router.get(..., dependencies=[Depends(require_role({'ADMIN'}))])
    """
    allowed: Set[str] = {str(r).upper() for r in required}

    def _checker(user: User = Depends(get_current_user)) -> User:
        user_role = _role_to_str(getattr(user, "role", ""))
        if allowed and user_role not in allowed:
            # Если у модели есть is_superadmin — пропустим супер-админа
            is_super = bool(getattr(user, "is_superadmin", False))
            if not is_super:
                raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _checker
