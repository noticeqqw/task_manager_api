import json
import asyncio
import hmac
import hashlib
from datetime import datetime
from typing import Optional
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import aiohttp

from app.core.retry_policy import MAX_RETRIES
from app.integrations.kafka.retry_producer import publish_retry
from app.db.session import SessionLocal
from app.models.webhook import Webhook
from app.models.webhook_delivery import WebhookDelivery
from app.core.config import settings


class AsyncWebhookConsumer:
    def __init__(self):
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.running = False
        
    async def start(self):
        """Инициализация и запуск consumer"""
        self.consumer = AIOKafkaConsumer(
            "tasks.events",
            "webhooks.retry.10s",
            "webhooks.retry.30s",
            "webhooks.retry.2m",
            "webhooks.retry.10m",
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="webhook-consumer-async",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        await self.consumer.start()
        await self.producer.start()
        self.running = True
        print("Async Webhook Consumer started")
        
    async def stop(self):
        """Остановка consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        print("Async Webhook Consumer stopped")
        
    def _sign_payload(self, secret: str, payload: dict) -> str:
        """Генерация HMAC подписи для webhook payload"""
        body = json.dumps(payload, sort_keys=True).encode()
        return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    
    async def dispatch_webhook_async(
        self, 
        webhook: Webhook, 
        event_type: str, 
        payload: dict
    ) -> tuple[bool, int, str]:
        """Асинхронная отправка webhook"""
        url = str(webhook.url)
        secret = str(webhook.secret)
        
        # Подготовка payload
        body = {
            "event": event_type,
            "data": payload
        }
        
        # Генерация HMAC подписи
        signature = self._sign_payload(secret, body)
        
        headers = {
            "Content-Type": "application/json",
            "X-Webhook-Event": event_type,
            "X-Webhook-Signature": f"sha256={signature}",
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=body,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_body = await response.text()
                    return (
                        200 <= response.status < 300,
                        response.status,
                        response_body[:500]  # Ограничиваем размер
                    )
        except asyncio.TimeoutError:
            return False, 0, "Timeout"
        except Exception as e:
            return False, 0, str(e)[:500]
    
    async def process_message(self, msg):
        """Обработка одного сообщения"""
        event = msg.value
        
        event_type = event.get("event_type")
        payload = event.get("payload", {})
        retry_count = event.get("retry_count", 0)
        next_attempt_at = event.get("next_attempt_at")
        
        if not event_type:
            print(f"Event missing event_type: {event}")
            return
        
        # Ждём, если рано
        if next_attempt_at:
            wait_seconds = (
                datetime.fromisoformat(next_attempt_at) - datetime.utcnow()
            ).total_seconds()
            
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
        
        # Работа с БД (синхронная)
        db = SessionLocal()
        try:
            webhooks = (
                db.query(Webhook)
                .filter(
                    Webhook.is_active == True,
                    Webhook.events.contains([event_type]),
                )
                .all()
            )
            
            # Обрабатываем все webhooks параллельно
            tasks = []
            for webhook in webhooks:
                task = self.process_webhook(
                    webhook, event_type, payload, retry_count, db
                )
                tasks.append(task)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        finally:
            db.close()
    
    async def process_webhook(
        self, 
        webhook: Webhook, 
        event_type: str, 
        payload: dict, 
        retry_count: int,
        db
    ):
        """Обработка одного webhook"""
        # Генерация idempotency key
        task_id = payload.get("task_id")
        idempotency_key = f"{webhook.id}:{event_type}:{task_id}:{retry_count}"
        
        # Проверка на дубликат
        existing_delivery = db.query(WebhookDelivery).filter(
            WebhookDelivery.idempotency_key == idempotency_key
        ).first()
        
        if existing_delivery:
            print(f"Skipping duplicate delivery: {idempotency_key}")
            return
        
        # Отправка webhook
        success, status_code, response_body = await self.dispatch_webhook_async(
            webhook, event_type, payload
        )
        
        # Сохранение результата
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
        
        # Retry логика
        if not success:
            retry_event = {
                "event_type": event_type,
                "payload": payload,
                "retry_count": retry_count + 1
            }
            
            if retry_count < MAX_RETRIES:
                await self.publish_retry(retry_event)
            else:
                # Dead Letter Queue
                if self.producer:
                    await self.producer.send("webhooks.dlq", value=retry_event)
    
    async def publish_retry(self, event: dict):
        """Публикация события для retry"""
        if not self.producer:
            print("Producer not available for retry")
            return
        
        retry_count = event.get("retry_count", 0)
        
        # Определение retry топика
        if retry_count == 1:
            topic = "webhooks.retry.10s"
        elif retry_count == 2:
            topic = "webhooks.retry.30s"
        elif retry_count == 3:
            topic = "webhooks.retry.2m"
        else:
            topic = "webhooks.retry.10m"
        
        await self.producer.send(topic, value=event)
    
    async def run(self):
        """Главный цикл обработки сообщений"""
        if not self.consumer:
            print("Consumer not started")
            return
        
        try:
            async for msg in self.consumer:
                try:
                    await self.process_message(msg)
                except Exception as e:
                    print(f"Error processing message: {e}")
        except asyncio.CancelledError:
            print("Consumer task cancelled")
        finally:
            await self.stop()


# Singleton instance
async_webhook_consumer = AsyncWebhookConsumer()
