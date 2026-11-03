from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from context import AssistantContext
from tasks.capability import TaskCapability
from tasks.models import Task


@dataclass(frozen=True, slots=True)
class TaskCognitiveResult:
    """Resultado de una consulta cognitiva sobre tareas."""

    tasks: tuple[Task, ...]
    metadata: dict[str, Any]


class TaskCognitiveAccess:
    """Punto de acceso cognitivo al subsistema Tasks."""

    def __init__(self, capability: TaskCapability) -> None:
        self._capability = capability

    def find_relevant(
        self,
        *,
        context: AssistantContext,
    ) -> TaskCognitiveResult:
        tasks = tuple(self._capability.relevant(context=context))
        return TaskCognitiveResult(
            tasks=tasks,
            metadata={
                "operation": "tasks.find_relevant",
                "count": len(tasks),
            },
        )

    def get(
        self,
        task_id: str,
        *,
        context: AssistantContext,
    ) -> Task | None:
        return self._capability.get(task_id, context=context)

    def list(
        self,
        *,
        context: AssistantContext,
    ) -> tuple[Task, ...]:
        return self._capability.list(context=context)
