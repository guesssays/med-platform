# backend/app/models/auth_tokens.py
from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # уникальный идентификатор refresh-токена (jti)
    jti: str = Column(String(64), nullable=False, unique=True, index=True)

    created_at: datetime = Column(
        DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    expires_at: datetime = Column(DateTime(timezone=True), nullable=False)

    revoked: bool = Column(Boolean, nullable=False, server_default="FALSE")

    user_agent: str | None = Column(String(256))
    ip: str | None = Column(String(64))

    # ВАЖНО: только back_populates, без backref
    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("ix_refresh_tokens_user_active", "user_id", "revoked"),
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # jti из reset JWT
    token_jti: str = Column(String(64), nullable=False, unique=True, index=True)

    created_at: datetime = Column(
        DateTime(timezone=True), nullable=False, server_default="CURRENT_TIMESTAMP"
    )
    expires_at: datetime = Column(DateTime(timezone=True), nullable=False)
    used: bool = Column(Boolean, nullable=False, server_default="FALSE")

    # ВАЖНО: только back_populates, без backref
    user = relationship("User", back_populates="password_reset_tokens")
