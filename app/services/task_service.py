from sqlalchemy.orm import Session
from uuid import UUID

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.core.events import EventTypes
from app.services.webhook_dispatcher import dispatch_webhook
from app.models.webhook import Webhook


def _trigger_webhooks(db: Session, event: str, task: Task):
    """Вспомогательная функция для отправки webhook уведомлений"""
    webhooks = db.query(Webhook).filter(
        Webhook.events.contains([event]),
        Webhook.is_active == True
    ).all()
    
    assignee_id_value = task.assignee_id
    payload = {
        "task_id": str(task.id),
        "title": str(task.title),
        "status": str(task.status),
        "creator_id": str(task.creator_id),
        "assignee_id": str(assignee_id_value) if assignee_id_value is not None else None,
    }
    
    for webhook in webhooks:
        try:
            dispatch_webhook(webhook, event, payload)
        except Exception as e:
            print(f"Webhook dispatch failed: {e}")


def create_task(db: Session, creator_id: UUID, data: TaskCreate) -> Task:
    task = Task(
        title=data.title,
        description=data.description,
        status=data.status,
        creator_id=creator_id,
        assignee_id=data.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Отправка webhook при создании задачи
    _trigger_webhooks(db, EventTypes.TASK_CREATED, task)
    
    return task


def get_task(db: Session, task_id: UUID):
    return db.query(Task).filter(Task.id == task_id).first()


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
    
    # Отправка webhook при обновлении задачи
    _trigger_webhooks(db, EventTypes.TASK_UPDATED, task)
    
    # Если статус изменился, отправляем дополнительный webhook
    if old_status != str(task.status):
        _trigger_webhooks(db, EventTypes.TASK_STATUS_CHANGED, task)
    
    return task

def delete_task(db: Session, task: Task):
    # Отправка webhook перед удалением
    _trigger_webhooks(db, EventTypes.TASK_DELETED, task)
    
    db.delete(task)
    db.commit()


