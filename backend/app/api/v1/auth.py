# app/api/v1/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    get_token_jti,
    REFRESH_EXPIRES_DAYS,
    RESET_TOKEN_EXPIRES_MIN,
)
from app.models.user import User
from app.models.auth_tokens import RefreshToken, PasswordResetToken  # убедись, что файл называется именно auth_tokens.py

router = APIRouter(prefix="/auth", tags=["auth"])

# ======== Security (Bearer) ========
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Получаем текущего пользователя из access-токена (Authorization: Bearer <access>).
    """
    if not credentials or not credentials.scheme.lower() == "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


# ======== Schemas ========

class AuthPayload(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshPayload(BaseModel):
    refresh_token: str


class LogoutPayload(BaseModel):
    refresh_token: str | None = None
    all_sessions: bool = False


class ForgotPayload(BaseModel):
    email: EmailStr


class ResetPayload(BaseModel):
    reset_token: str
    new_password: str


class ChangePasswordPayload(BaseModel):
    current_password: str
    new_password: str


# ======== Helpers ========

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _refresh_exp_dt() -> datetime:
    return _utcnow() + timedelta(days=REFRESH_EXPIRES_DAYS)


def _reset_exp_dt() -> datetime:
    return _utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRES_MIN)


# ======== Endpoints ========

@router.post("/register", response_model=TokenPair)
def register(payload: AuthPayload, request: Request, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.email).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    # issue tokens + persist refresh
    refresh = create_refresh_token(user.email)
    jti = get_token_jti(refresh)
    rt = RefreshToken(
        user_id=user.id,
        jti=jti,
        expires_at=_refresh_exp_dt(),
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host if request.client else None,
    )
    db.add(rt)
    db.commit()

    return TokenPair(
        access_token=create_access_token({"sub": user.email}),
        refresh_token=refresh,
    )


@router.post("/login", response_model=TokenPair)
def login(payload: AuthPayload, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash or ""):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    # rotate refresh (new jti each login)
    refresh = create_refresh_token(user.email)
    jti = get_token_jti(refresh)
    rt = RefreshToken(
        user_id=user.id,
        jti=jti,
        expires_at=_refresh_exp_dt(),
        user_agent=request.headers.get("user-agent"),
        ip=request.client.host if request.client else None,
    )
    db.add(rt)
    db.commit()

    return TokenPair(
        access_token=create_access_token({"sub": user.email}),
        refresh_token=refresh,
    )


@router.post("/refresh", response_model=TokenPair)
def refresh(body: RefreshPayload, request: Request, db: Session = Depends(get_db)):
    # 1) decode & basic checks
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")
    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 2) ensure jti is whitelisted and not revoked/expired
    db_rt = db.query(RefreshToken).filter(RefreshToken.jti == jti, RefreshToken.user_id == user.id).first()
    if not db_rt or db_rt.revoked or db_rt.expires_at <= _utcnow():
        raise HTTPException(status_code=401, detail="Refresh token is invalid or expired")

    # 3) rotate refresh token (recommended)
    db_rt.revoked = True
    new_refresh = create_refresh_token(user.email)
    new_jti = get_token_jti(new_refresh)
    db.add(
        RefreshToken(
            user_id=user.id,
            jti=new_jti,
            expires_at=_refresh_exp_dt(),
            user_agent=request.headers.get("user-agent"),
            ip=request.client.host if request.client else None,
        )
    )
    db.commit()

    return TokenPair(
        access_token=create_access_token({"sub": user.email}),
        refresh_token=new_refresh,
    )


@router.post("/logout")
def logout(body: LogoutPayload, db: Session = Depends(get_db)):
    """
    Если передан refresh_token — ревокируем конкретную сессию.
    Если all_sessions=True — ревокируем все активные refresh пользователя из этого токена.
    """
    if body.all_sessions and not body.refresh_token:
        raise HTTPException(status_code=400, detail="Provide refresh_token to revoke all sessions for its user")

    if not body.refresh_token:
        return {"status": "ok"}  # мягкий logout (клиент просто забывает токены)

    try:
        payload = decode_token(body.refresh_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid token type")
    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if body.all_sessions:
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked == False,  # noqa: E712
        ).update({"revoked": True})
        db.commit()
        return {"status": "ok", "revoked": "all"}
    else:
        rt = db.query(RefreshToken).filter(RefreshToken.jti == jti, RefreshToken.user_id == user.id).first()
        if rt and not rt.revoked:
            rt.revoked = True
            db.commit()
        return {"status": "ok", "revoked": "single"}


@router.post("/password/forgot")
def forgot_password(body: ForgotPayload, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        # не палим существование пользователя
        return {"status": "ok"}

    reset_token = create_reset_token(user.email)
    # сохраняем в БД jti + срок
    jti = get_token_jti(reset_token)
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_jti=jti,
            expires_at=_reset_exp_dt(),
        )
    )
    db.commit()

    # здесь можно отправить письмо. Пока — просто логируем в stdout (или Docker-логи).
    print(f"[DEV] Password reset token for {user.email}: {reset_token}")
    return {"status": "ok"}


@router.post("/password/reset")
def reset_password(body: ResetPayload, db: Session = Depends(get_db)):
    try:
        payload = decode_token(body.reset_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid reset token")

    if payload.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid token type")
    sub = payload.get("sub")
    jti = payload.get("jti")
    if not sub or not jti:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db_rec = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_jti == jti,
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used == False,  # noqa: E712
    ).first()

    if not db_rec or db_rec.expires_at <= _utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired or invalid")

    # set new password
    user.password_hash = get_password_hash(body.new_password)
    db_rec.used = True
    # (опционально) инвалидировать все refresh-токены пользователя:
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False,  # noqa: E712
    ).update({"revoked": True})

    db.commit()
    return {"status": "ok"}


@router.post("/password/change")
def change_password(
    body: ChangePasswordPayload,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # теперь работаем через access_token из Authorize
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password invalid")

    user.password_hash = get_password_hash(body.new_password)

    # ревокируем все refresh
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False,  # noqa: E712
    ).update({"revoked": True})

    db.commit()
    return {"status": "ok"}
