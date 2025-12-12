class EventTypes:
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_DELETED = "task.deleted"
    TASK_STATUS_CHANGED = "task.status_changed"

    ALL = {
        TASK_CREATED,
        TASK_UPDATED,
        TASK_DELETED,
        TASK_STATUS_CHANGED,
    }
