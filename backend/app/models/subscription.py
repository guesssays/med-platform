from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text("true"))
    started_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    expires_at = Column(DateTime)

    patient = relationship("PatientProfile", back_populates="subscriptions")
    doctor = relationship("DoctorProfile", back_populates="subscriptions")
