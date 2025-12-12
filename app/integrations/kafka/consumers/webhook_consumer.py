import json
from confluent_kafka import Consumer, Producer
import time
from datetime import datetime

from app.core.retry_policy import RETRY_TOPICS, MAX_RETRIES
from app.integrations.kafka.retry_producer import publish_retry

from app.db.session import SessionLocal
from app.models.webhook import Webhook
from app.models.webhook_delivery import WebhookDelivery
from app.services.webhook_dispatcher import dispatch_webhook

MAX_RETRIES = 5

consumer = Consumer(
    {
        "bootstrap.servers": "kafka:9092",
        "group.id": "webhook-consumer",
        "auto.offset.reset": "earliest",
    }
)

producer = Producer({"bootstrap.servers": "kafka:9092"})

consumer.subscribe(
    [
        "tasks.events",
        "webhooks.retry.10s",
        "webhooks.retry.30s",
        "webhooks.retry.2m",
        "webhooks.retry.10m",
    ]
)

def publish(topic: str, event: dict):
    producer.produce(topic, json.dumps(event).encode())
    producer.flush()


def run():
    while True:
        msg = consumer.poll(1.0)
        if not msg:
            continue
        if msg.error():
            print(msg.error())
            continue

        event = json.loads(msg.value().decode())

        event_type = event.get("event_type")
        payload = event.get("payload", {})
        retry_count = event.get("retry_count", 0)
        next_attempt_at = event.get("next_attempt_at")

        if not event_type:
            print(f"Event missing event_type: {event}")
            continue

        # ⏱ ЖДЁМ, ЕСЛИ РАНО
        if next_attempt_at:
            wait_seconds = (
                datetime.fromisoformat(next_attempt_at) - datetime.utcnow()
            ).total_seconds()

            if wait_seconds > 0:
                time.sleep(wait_seconds)

        db = SessionLocal()

        webhooks = (
            db.query(Webhook)
            .filter(
                Webhook.is_active == True,
                Webhook.events.contains([event_type]),
            )
            .all()
        )

        for webhook in webhooks:
            # Генерация idempotency key: webhook_id + event_type + task_id
            task_id = payload.get("task_id")
            idempotency_key = f"{webhook.id}:{event_type}:{task_id}:{retry_count}"
            
            # Проверка на дубликат
            existing_delivery = db.query(WebhookDelivery).filter(
                WebhookDelivery.idempotency_key == idempotency_key
            ).first()
            
            if existing_delivery:
                print(f"Skipping duplicate delivery: {idempotency_key}")
                continue
            
            success, status_code, response_body = dispatch_webhook(
                webhook,
                event_type,
                payload,
            )

            delivery = WebhookDelivery(
                webhook_id=webhook.id,
                idempotency_key=idempotency_key,
                event=event_type,
                payload=payload,
                status_code=status_code,
                response_body=response_body,
                attempt=retry_count + 1,
            )
            db.add(delivery)
            db.commit()

            if success:
                continue

            if retry_count < MAX_RETRIES:
                event["retry_count"] += 1
                publish_retry(event)
            else:
                publish("webhooks.dlq", event)

        db.close()
