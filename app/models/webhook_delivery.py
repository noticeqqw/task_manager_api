import uuid
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id"))
    idempotency_key = Column(String, unique=True, nullable=False, index=True)
    event = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)

    status_code = Column(Integer)
    response_body = Column(String)

    attempt = Column(Integer, nullable=False)
    delivered_at = Column(DateTime, default=datetime.utcnow)
