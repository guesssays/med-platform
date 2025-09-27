from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create(db: Session, *, email: str, password: str, phone: str | None, role: str = "patient") -> User:
    user = User(
        email=email,
        phone=phone,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
