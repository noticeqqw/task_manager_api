import json
import uuid
from datetime import datetime

from confluent_kafka import Producer

producer = Producer(
    {
        "bootstrap.servers": "kafka:9092",
    }
)


def publish_event(topic: str, event_type: str, payload: dict):
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.utcnow().isoformat(),
        "payload": payload,
    }

    producer.produce(
        topic=topic,
        value=json.dumps(event).encode(),
    )
    producer.flush()
