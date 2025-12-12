import secrets
from sqlalchemy.orm import Session

from app.models.webhook import Webhook
from app.schemas.webhook import WebhookCreate


def create_webhook(db: Session, user_id, data: WebhookCreate) -> Webhook:
    secret = secrets.token_hex(32)

    webhook = Webhook(
        user_id=user_id,
        url=str(data.url),
        secret=secret,
        events=data.events,
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


def get_user_webhooks(db: Session, user_id):
    return db.query(Webhook).filter(Webhook.user_id == user_id).all()
