import hmac
import hashlib
import json
import requests


def sign_payload(secret: str, payload: dict) -> str:
    body = json.dumps(payload).encode()
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def dispatch_webhook(webhook, event_type: str, payload: dict) -> tuple[bool, int | None, str | None]:
    signature = sign_payload(webhook.secret, payload)

    headers = {
        "X-Event-Type": event_type,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            webhook.url,
            json=payload,
            headers=headers,
            timeout=5,
        )
        success = 200 <= response.status_code < 300
        return success, response.status_code, response.text[:1000]
    except requests.RequestException as e:
        return False, None, str(e)
