from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey("doctor_profiles.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patient_profiles.id"), nullable=False)
    starts_at = Column(DateTime, nullable=False)
    ends_at = Column(DateTime, nullable=False)
    status = Column(String(32), nullable=False, server_default="scheduled")

    doctor = relationship("DoctorProfile", back_populates="appointments")
    patient = relationship("PatientProfile", back_populates="appointments")
