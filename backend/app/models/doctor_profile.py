from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class DoctorProfile(Base):
    __tablename__ = "doctor_profiles"

    id: int = Column(Integer, primary_key=True, index=True)

    # связь 1–1 с пользователем
    user_id: int = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    user = relationship("User", back_populates="doctor_profile")

    # связь многие–к–одному с клиникой (опционально)
    clinic_id: int | None = Column(
        Integer,
        ForeignKey("clinics.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    clinic = relationship("Clinic", back_populates="doctor_profiles")

    # актуальное поле из миграций
    title: str | None = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"<DoctorProfile id={self.id} user_id={self.user_id} clinic_id={self.clinic_id}>"
