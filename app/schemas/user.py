from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    role: str | None = "user"
    is_active: bool | None = True


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: UUID

    class Config:
        from_attributes = True
