from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.admin import router as admin_router
from app.api.teams import router as teams_router
from app.integrations.kafka.consumers.async_webhook_consumer import async_webhook_consumer
from app.services.async_kafka_producer import async_kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management для FastAPI"""
    # Startup
    await async_kafka_producer.start()
    await async_webhook_consumer.start()
    consumer_task = asyncio.create_task(async_webhook_consumer.run())
    
    yield
    
    # Shutdown
    consumer_task.cancel()
    await async_webhook_consumer.stop()
    await async_kafka_producer.stop()


app = FastAPI(
    title="Task Manager API",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(admin_router)
app.include_router(teams_router)

@app.get("/health")
def health():
    return {"status": "ok"}
