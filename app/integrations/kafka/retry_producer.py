import json
from datetime import datetime, timedelta
from confluent_kafka import Producer

from app.core.retry_policy import RETRY_TOPICS

producer = Producer({"bootstrap.servers": "kafka:9092"})


def publish_retry(event: dict):
    retry_count = event["retry_count"]

    topic, delay = RETRY_TOPICS[retry_count]

    event["next_attempt_at"] = (
        datetime.utcnow() + timedelta(seconds=delay)
    ).isoformat()

    producer.produce(topic, json.dumps(event).encode())
    producer.flush()
