from __future__ import annotations

from tasks.models import Task


class TaskStore:
    """In-memory store for assistant tasks."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> Task:
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def list(self) -> list[Task]:
        return list(self._tasks.values())

    def update(self, task: Task) -> Task:
        if task.id not in self._tasks:
            raise KeyError(f"Task not found: {task.id}")

        self._tasks[task.id] = task
        return task

    def remove(self, task_id: str) -> Task | None:
        return self._tasks.pop(task_id, None)

    def clear(self) -> None:
        self._tasks.clear()

    def count(self) -> int:
        return len(self._tasks)
