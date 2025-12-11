from uuid import UUID
from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    pass


class TeamRead(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
