from datetime import datetime, timedelta, timezone
import os
from typing import Dict, Any, Union
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext

try:
    from app.core.config import settings  # type: ignore

    JWT_SECRET = getattr(settings, "JWT_SECRET", None) or os.getenv("JWT_SECRET", "dev-secret")
    JWT_ALG = getattr(settings, "JWT_ALG", None) or os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRES_MIN", str(getattr(settings, "JWT_EXPIRES_MIN", 60))))
    REFRESH_EXPIRES_DAYS = int(os.getenv("REFRESH_EXPIRES_DAYS", str(getattr(settings, "REFRESH_EXPIRES_DAYS", 30))))
    RESET_TOKEN_EXPIRES_MIN = int(os.getenv("RESET_TOKEN_EXPIRES_MIN", str(getattr(settings, "RESET_TOKEN_EXPIRES_MIN", 30))))
except Exception:
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
    JWT_ALG = os.getenv("JWT_ALG", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRES_MIN", "60"))
    REFRESH_EXPIRES_DAYS = int(os.getenv("REFRESH_EXPIRES_DAYS", "30"))
    RESET_TOKEN_EXPIRES_MIN = int(os.getenv("RESET_TOKEN_EXPIRES_MIN", "30"))

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return pwd_context.verify((plain_password or "")[:72], password_hash or "")
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash((password or "")[:72])


def _jwt_now_exp(minutes: int) -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=minutes)
    return int(now.timestamp()), int(exp.timestamp())


def _jwt_exp_in_days(days: int) -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=days)
    return int(now.timestamp()), int(exp.timestamp())


def create_access_token(subject: Union[str, Dict[str, Any]], expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    _, exp = _jwt_now_exp(expires_minutes)
    payload: Dict[str, Any]
    if isinstance(subject, dict):
        payload = dict(subject)
    else:
        payload = {"sub": str(subject)}
    payload["exp"] = exp
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_refresh_token(user_email: str, jti: str | None = None) -> str:
    """Refresh-токен: sub=email, jti=UUID, срок жизни в днях."""
    _, exp = _jwt_exp_in_days(REFRESH_EXPIRES_DAYS)
    payload: Dict[str, Any] = {"sub": user_email, "type": "refresh", "jti": jti or str(uuid.uuid4()), "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_reset_token(user_email: str) -> str:
    """Токен для сброса пароля (короткоживущий)."""
    _, exp = _jwt_now_exp(RESET_TOKEN_EXPIRES_MIN)
    payload: Dict[str, Any] = {"sub": user_email, "type": "reset", "exp": exp, "jti": str(uuid.uuid4())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])


def get_token_jti(token: str) -> str | None:
    try:
        payload = decode_token(token)
        return payload.get("jti")
    except JWTError:
        return None
