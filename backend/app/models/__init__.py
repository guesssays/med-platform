# Важно: импортируй все модели, чтобы они попали в мапперы
from .user import User
from .clinic import Clinic
from .doctor_profile import DoctorProfile

__all__ = ["User", "Clinic", "DoctorProfile"]
