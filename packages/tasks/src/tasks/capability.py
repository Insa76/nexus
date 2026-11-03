from __future__ import annotations

from dataclasses import dataclass

from context import AssistantContext

from tasks.models import Task
from tasks.resolver import TaskResolver
from tasks.store import TaskStore


@dataclass(slots=True)
class TaskCapability:
    """Interfaz de acceso a tareas respetando el contexto activo."""

    store: TaskStore
    resolver: TaskResolver

    def create(
        self,
        *,
        title: str,
        description: str | None = None,
        priority: str = "normal",
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> Task:
        task = Task.create(
            title=title,
            description=description,
            priority=priority,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )
        return self.store.add(task)

    def get(
        self,
        task_id: str,
        *,
        context: AssistantContext,
    ) -> Task | None:
        return next(
            (
                task
                for task in self.resolver.resolve(context)
                if task.id == task_id
            ),
            None,
        )

    def list(
        self,
        *,
        context: AssistantContext,
    ) -> tuple[Task, ...]:
        return tuple(self.resolver.resolve(context))

    def relevant(
        self,
        *,
        context: AssistantContext,
    ) -> list[Task]:
        return self.resolver.resolve(context)
