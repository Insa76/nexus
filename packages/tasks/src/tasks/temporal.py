from __future__ import annotations

from datetime import datetime

from tasks.models import Task


def overdue_tasks(
    tasks: list[Task],
    now: datetime,
) -> list[Task]:
    return [
        task
        for task in tasks
        if task.due_at is not None
        and task.due_at < now
        and task.status not in {"completed", "cancelled"}
    ]


def due_tasks(
    tasks: list[Task],
    now: datetime,
) -> list[Task]:
    return [
        task
        for task in tasks
        if task.due_at is not None
        and task.due_at <= now
        and task.status not in {"completed", "cancelled"}
    ]


def upcoming_tasks(
    tasks: list[Task],
    now: datetime,
) -> list[Task]:
    return [
        task
        for task in tasks
        if task.due_at is not None
        and task.due_at > now
        and task.status not in {"completed", "cancelled"}
    ]
