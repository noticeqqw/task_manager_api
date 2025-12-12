import json
from typing import Any, Dict, Optional
from aiokafka import AIOKafkaProducer
from app.core.config import settings


class AsyncKafkaEventProducer:
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
    
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id='task-manager-async-producer',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        await self.producer.start()
        print("Async Kafka Producer started")
    
    async def stop(self):
        if self.producer:
            await self.producer.stop()
            print("Async Kafka Producer stopped")
    
    async def publish_event(self, topic: str, event_type: str, payload: Dict[str, Any]):
        if not self.producer:
            print("Producer not started, cannot publish event")
            return
        
        message = {
            'event_type': event_type,
            'payload': payload
        }
        
        try:
            await self.producer.send(
                topic=topic,
                key=event_type,
                value=message
            )
        except Exception as e:
            print(f"Failed to publish event to Kafka: {e}")


# Singleton instance
async_kafka_producer = AsyncKafkaEventProducer()
