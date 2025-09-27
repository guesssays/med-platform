from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ContentItem(Base):
    __tablename__ = "content_items"

    id = Column(Integer, primary_key=True)
    author_doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    kind = Column(String(32), nullable=False)
    body = Column(Text)
    r2_key = Column(String(512))
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    author_doctor = relationship("DoctorProfile", back_populates="contents")
