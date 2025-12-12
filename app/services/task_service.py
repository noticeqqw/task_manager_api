from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
import asyncio

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.events import EventTypes
from app.services.async_kafka_producer import async_kafka_producer
from app.core.config import settings


def _publish_task_event(event_type: str, task: Task):
    """Публикация события задачи в Kafka (синхронная обертка)"""
    assignee_id_value = task.assignee_id
    payload = {
        "task_id": str(task.id),
        "title": str(task.title),
        "status": str(task.status),
        "creator_id": str(task.creator_id),
        "assignee_id": str(assignee_id_value) if assignee_id_value is not None else None,
    }
    
    try:
        # Создаем event loop если его нет, или используем существующий
        try:
            loop = asyncio.get_running_loop()
            # Если мы в async контексте, создаем task
            asyncio.create_task(
                async_kafka_producer.publish_event(
                    topic=settings.KAFKA_TOPIC_TASKS,
                    event_type=event_type,
                    payload=payload
                )
            )
        except RuntimeError:
            # Если мы не в async контексте, используем run_until_complete
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                async_kafka_producer.publish_event(
                    topic=settings.KAFKA_TOPIC_TASKS,
                    event_type=event_type,
                    payload=payload
                )
            )
    except Exception as e:
        print(f"Failed to publish task event: {e}")


def create_task(
    db: Session, 
    creator_id: UUID, 
    data: TaskCreate, 
    idempotency_key: Optional[str] = None
) -> Task:
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        creator_id=creator_id,
        assignee_id=data.assignee_id,
        idempotency_key=idempotency_key,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Публикация события в Kafka
    _publish_task_event(EventTypes.TASK_CREATED, task)
    
    return task


def get_task(db: Session, task_id: UUID):
    return db.query(Task).filter(Task.id == task_id).first()


def get_task_by_idempotency_key(db: Session, idempotency_key: str):
    """Получение задачи по idempotency key для предотвращения дублирования"""
    return db.query(Task).filter(Task.idempotency_key == idempotency_key).first()


def get_tasks(db: Session, creator_id: UUID | None = None):
    q = db.query(Task)
    if creator_id:
        q = q.filter(Task.creator_id == creator_id)
    return q.all()


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    old_status = str(task.status)
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    
    # Публикация события в Kafka
    _publish_task_event(EventTypes.TASK_UPDATED, task)
    
    # Если статус изменился, публикуем дополнительное событие
    if old_status != str(task.status):
        _publish_task_event(EventTypes.TASK_STATUS_CHANGED, task)
    
    return task

def delete_task(db: Session, task: Task):
    # Публикация события в Kafka перед удалением
    _publish_task_event(EventTypes.TASK_DELETED, task)
    
    db.delete(task)
    db.commit()


