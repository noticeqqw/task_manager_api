from datetime import datetime
from typing import Any
from pydantic import BaseModel


class Event(BaseModel):
    event_id: str
    event_type: str
    occurred_at: datetime
    payload: dict[str, Any]

    retry_count: int = 0
    next_attempt_at: datetime | None = None
