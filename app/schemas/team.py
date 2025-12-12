from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamRead(BaseModel):
    id: UUID
    name: str
    owner_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class TeamMemberRead(BaseModel):
    id: UUID
    email: str
    role: str

    class Config:
        from_attributes = True


class TeamMemberUpdate(BaseModel):
    role: str
