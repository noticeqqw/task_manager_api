from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, creator_id, data: TaskCreate) -> Task:
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
    return task


def get_task(db: Session, task_id):
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks(db: Session, creator_id=None):
    q = db.query(Task)
    if creator_id:
        q = q.filter(Task.creator_id == creator_id)
    return q.all()


def update_task(db: Session, task: Task, data: TaskUpdate) -> Task:
    for field, value in data.dict(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task):
    db.delete(task)
    db.commit()
