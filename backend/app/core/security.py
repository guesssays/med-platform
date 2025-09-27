# app/core/security.py
from datetime import datetime, timedelta, timezone
import os
from typing import Dict, Any, Union

from jose import jwt, JWTError
from passlib.context import CryptContext

# Берём конфиг как в deps.py: сначала settings, иначе ENV, иначе дефолт
try:
    from app.core.config import settings  # type: ignore
    JWT_SECRET = getattr(settings, "JWT_SECRET", None) or os.getenv("JWT_SECRET", "dev-secret")
    JWT_ALG = getattr(settings, "JWT_ALG", None) or os.getenv("JWT_ALG", "HS256")
except Exception:
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
    JWT_ALG = os.getenv("JWT_ALG", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 дней по умолчанию

# Пароли — PBKDF2 (как ты указал)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        # ограничение длины как у тебя, на всякий случай
        return pwd_context.verify((plain_password or "")[:72], password_hash or "")
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    return pwd_context.hash((password or "")[:72])


def create_access_token(subject: Union[str, Dict[str, Any]], expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """
    Если subject — str, кладём в sub. Если dict, копируем и добавляем exp.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expires_minutes)

    if isinstance(subject, dict):
        payload = dict(subject)
        payload["exp"] = int(exp.timestamp())
    else:
        payload = {"sub": str(subject), "exp": int(exp.timestamp())}

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Dict[str, Any]:
    # используем те же секрет/алгоритм
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
