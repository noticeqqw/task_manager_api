from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


def create_user(db: Session, user_in: UserCreate) -> User:
    try:
        hashed_pwd = hash_password(user_in.password)
    except Exception as e:
        raise RuntimeError(f"Password hashing failed: {str(e)}")
    
    user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        role="user",
        is_active=True,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email already exists")

    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()