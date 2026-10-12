from __future__ import annotations

from tasks.models import Task, TaskStatus


_ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED,
    },
    TaskStatus.IN_PROGRESS: {
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set(),
}


class InvalidTaskTransition(ValueError):
    """Raised when a task lifecycle transition is not allowed."""


def can_transition(
    current: TaskStatus,
    target: TaskStatus,
) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def transition_task(
    task: Task,
    target: TaskStatus,
) -> Task:
    if not can_transition(task.status, target):
        raise InvalidTaskTransition(
            f"Invalid task transition: "
            f"{task.status.value} -> {target.value}"
        )

    return Task(
        id=task.id,
        title=task.title,
        description=task.description,
        status=target,
        priority=task.priority,
        user_id=task.user_id,
        organization_id=task.organization_id,
        project_id=task.project_id,
        due_at=task.due_at,
        created_at=task.created_at,
    )
