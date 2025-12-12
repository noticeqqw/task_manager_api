from pydantic import BaseModel, HttpUrl
from uuid import UUID
from typing import List


class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]


class WebhookRead(BaseModel):
    id: UUID
    url: HttpUrl
    events: List[str]
    is_active: bool

    class Config:
        from_attributes = True
