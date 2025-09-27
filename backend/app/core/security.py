# app/core/security.py
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

# !!! В проде вынесите в ENV
SECRET_KEY = "dev-secret-change-me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Уходим от bcrypt (были проблемы) — используем PBKDF2
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify((plain_password or "")[:72], password_hash or "")

def get_password_hash(password: str) -> str:
    return pwd_context.hash((password or "")[:72])

def create_access_token(data: Dict[str, Any], expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        # пробросим дальше — обработаем в deps
        raise

# FastAPI OAuth2 bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
