from uuid import UUID
from pydantic import BaseModel, EmailStr


class AdminUserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    team_id: UUID | None = None


class AdminUserRead(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    is_active: bool
    team_id: UUID | None

    class Config:
        from_attributes = True
