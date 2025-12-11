from uuid import UUID
from app.core.roles import Roles
from app.models.user import User
from app.models.task import Task


def is_admin(user: User) -> bool:
    return str(user.role) == Roles.ADMIN


def is_manager(user: User) -> bool:
    return str(user.role) == Roles.MANAGER


def is_user(user: User) -> bool:
    return str(user.role) == Roles.USER


def can_view_task(user: User, task: Task) -> bool:
    # admin видит всё
    if is_admin(user):
        return True

    # manager видит задачи своей команды
    if is_manager(user):
        return (
            task.creator.team_id == user.team_id
            or task.assignee and task.assignee.team_id == user.team_id
        )

    # user видит только свои
    return UUID(str(task.creator_id)) == user.id or UUID(str(task.assignee_id)) == user.id

def can_edit_task(user: User, task: Task) -> bool:
    # admin/manager могут редактировать всё
    if is_admin(user) or is_manager(user):
        return True

    # user может править только свои задачи (созданные им)
    return UUID(str(task.creator_id)) == UUID(str(user.id))


def can_delete_task(user: User, task: Task) -> bool:
    # пока равно правилам редактирования
    return can_edit_task(user, task)
