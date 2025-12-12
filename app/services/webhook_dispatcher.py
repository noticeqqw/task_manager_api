import hmac
import hashlib
import json
import requests

from app.models.webhook import Webhook
from app.models.webhook_delivery import WebhookDelivery
from app.db.session import SessionLocal


def sign_payload(secret: str, payload: dict) -> str:
    body = json.dumps(payload).encode()
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def dispatch_webhook(webhook: Webhook, event: str, payload: dict):
    signature = sign_payload(str(webhook.secret), payload)

    headers = {
        "X-Event-Type": event,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }

    response = requests.post(
        str(webhook.url),
        json=payload,
        headers=headers,
        timeout=5,
    )

    db = SessionLocal()
    delivery = WebhookDelivery(
        webhook_id=webhook.id,
        event=event,
        payload=payload,
        status_code=response.status_code,
        response_body=response.text[:1000],
    )
    db.add(delivery)
    db.commit()
    db.close()
