"""
Импортируй здесь все модели, чтобы Alembic видел их в metadata.
"""
from app.db.base_class import Base  # noqa: F401

# Пользователи и профили
from app.models.user import User  # noqa: F401

# Если есть другие модели (doctor_profiles, clinics, и т.д.), импортируй их по аналогии
try:
    from app.models.doctor_profile import DoctorProfile  # noqa: F401
except Exception:
    pass

try:
    from app.models.clinic import Clinic  # noqa: F401
except Exception:
    pass

# Токены аутентификации
from app.models.auth_tokens import RefreshToken, PasswordResetToken  # noqa: F401
