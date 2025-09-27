from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(64), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(8), nullable=False, server_default="UZS")
    status = Column(String(32), nullable=False, server_default="pending")
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User")
