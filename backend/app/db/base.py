# чтобы Alembic/SQLAlchemy увидели модели
from app.db.base_class import Base  # noqa: F401
from app.models import User, Clinic, DoctorProfile  # noqa: F401
