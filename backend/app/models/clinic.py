from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False, index=True)

    # новые поля, которые видели в автогенерации alembic
    address: str | None = Column(String, nullable=True)
    phone: str | None = Column(String, nullable=True)
    description: str | None = Column(String, nullable=True)

    # one-to-many к DoctorProfile
    doctor_profiles = relationship(
        "DoctorProfile",
        back_populates="clinic",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Clinic id={self.id} name={self.name!r}>"
