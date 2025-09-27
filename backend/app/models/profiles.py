from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    clinic_id: Mapped[int | None] = mapped_column(ForeignKey("clinics.id"))
    specialty: Mapped[str | None] = mapped_column(String(255))

    user = relationship("User", back_populates="doctor_profile")
    clinic = relationship("Clinic", back_populates="doctors")

class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="patient_profile")
