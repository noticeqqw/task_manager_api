from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.deps import get_db
from app.api.deps_auth import get_current_user
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.task_service import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task,
)
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=TaskRead)
def create_task_endpoint(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(db, creator_id=current_user.id, data=data)


@router.get("/", response_model=list[TaskRead])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_tasks(db, creator_id=current_user.id)


@router.get("/{task_id}", response_model=TaskRead)
def get_task_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if UUID(str(task.creator_id)) != UUID(str(current_user.id)):
        raise HTTPException(status_code=403, detail="Forbidden")

    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task_endpoint(
    task_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if UUID(str(task.creator_id)) != UUID(str(current_user.id)):
        raise HTTPException(status_code=403, detail="Forbidden")

    return update_task(db, task, data)


@router.delete("/{task_id}")
def delete_task_endpoint(
    task_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if UUID(str(task.creator_id)) != UUID(str(current_user.id)):
        raise HTTPException(status_code=403, detail="Forbidden")

    delete_task(db, task)
    return {"detail": "Task deleted"}
