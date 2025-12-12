import json
from typing import Any, Dict
from confluent_kafka import Producer
from app.core.config import settings


class KafkaEventProducer:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'client.id': 'task-manager-producer'
        })
    
    def publish_event(self, topic: str, event_type: str, payload: Dict[str, Any]):
        message = {
            'event_type': event_type,
            'payload': payload
        }
        
        try:
            self.producer.produce(
                topic=topic,
                key=event_type.encode('utf-8'),
                value=json.dumps(message).encode('utf-8'),
                callback=self._delivery_callback
            )
            self.producer.poll(0)  # Trigger delivery reports
        except Exception as e:
            print(f"Failed to publish event to Kafka: {e}")
    
    def _delivery_callback(self, err, msg):
        if err:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
    
    def flush(self):
        self.producer.flush()


# Singleton instance
kafka_producer = KafkaEventProducer()
