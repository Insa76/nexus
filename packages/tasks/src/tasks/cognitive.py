from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from context import AssistantContext
from tasks.capability import TaskCapability
from tasks.models import Task, TaskStatus


@dataclass(frozen=True, slots=True)
class TaskCognitiveResult:
    """Resultado de una consulta cognitiva sobre tareas."""

    tasks: tuple[Task, ...]
    metadata: dict[str, Any]


class TaskCognitiveAccess:
    """Punto de acceso cognitivo al subsistema Tasks."""

    def __init__(self, capability: TaskCapability) -> None:
        self._capability = capability

    def find_relevant(self, *, context: AssistantContext) -> TaskCognitiveResult:
        tasks = tuple(self._capability.relevant(context=context))
        return TaskCognitiveResult(
            tasks=tasks,
            metadata={"operation": "tasks.find_relevant", "count": len(tasks)},
        )

    def get(self, task_id: str, *, context: AssistantContext) -> Task | None:
        return self._capability.get(task_id, context=context)

    def list(self, *, context: AssistantContext) -> tuple[Task, ...]:
        return self._capability.list(context=context)

    def create(
        self, *, context: AssistantContext, title: str,
        description: str | None = None, priority: str = "normal",
    ) -> Task:
        return self._capability.create_for_context(
            title=title, description=description, priority=priority,
            context=context,
        )

    def update(
        self, task_id: str, *, context: AssistantContext,
        title: str | None = None, description: str | None = None,
        priority: str | None = None,
    ) -> Task | None:
        return self._capability.update_for_context(
            task_id, context=context, title=title,
            description=description, priority=priority,
        )

    def transition(
        self, task_id: str, target: TaskStatus, *, context: AssistantContext,
    ) -> Task | None:
        return self._capability.transition(task_id, target, context=context)
