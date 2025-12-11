from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps_auth import require_admin
from app.db.deps import get_db
from app.models.user import User
from app.schemas.admin_user import AdminUserRead, AdminUserUpdate

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.get("/", response_model=list[AdminUserRead])
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(User).all()


@router.get("/{user_id}", response_model=AdminUserRead)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    return user


@router.patch("/{user_id}", response_model=AdminUserRead)
def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
