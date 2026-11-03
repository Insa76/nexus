from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from context import AssistantContext, project_ids_for_context
from tasks.lifecycle import transition_task
from tasks.models import Task, TaskStatus
from tasks.resolver import TaskResolver
from tasks.store import TaskStore


@dataclass(slots=True)
class TaskCapability:
    """Interfaz de acceso a tareas respetando el contexto activo."""

    store: TaskStore
    resolver: TaskResolver

    def create(
        self, *, title: str, description: str | None = None,
        priority: str = "normal", user_id: str | None = None,
        organization_id: str | None = None, project_id: str | None = None,
        due_at: datetime | None = None,
    ) -> Task:
        task = Task.create(
            title=title, description=description, priority=priority,
            user_id=user_id, organization_id=organization_id,
            project_id=project_id, due_at=due_at,
        )
        return self.store.add(task)

    def create_for_context(
        self, *, title: str, context: AssistantContext,
        description: str | None = None, priority: str = "normal",
        due_at: datetime | None = None,
    ) -> Task:
        """Crea una tarea usando exclusivamente la identidad del contexto activo."""
        user = context.user
        organization = context.organization
        active_project_id = context.metadata.get("active_project_id")
        allowed_projects = project_ids_for_context(context)
        if active_project_id is not None and active_project_id not in allowed_projects:
            raise ValueError("El proyecto activo no pertenece al contexto actual.")
        return self.create(
            title=title, description=description, priority=priority,
            user_id=user.id if user is not None else None,
            organization_id=organization.id if organization is not None else None,
            project_id=active_project_id, due_at=due_at,
        )

    def transition(
        self, task_id: str, target: TaskStatus, *, context: AssistantContext,
    ) -> Task | None:
        task = self.get(task_id, context=context)
        if task is None:
            return None
        return self.store.update(transition_task(task, target))

    def get(self, task_id: str, *, context: AssistantContext) -> Task | None:
        return next(
            (task for task in self.resolver.resolve(context) if task.id == task_id),
            None,
        )

    def list(self, *, context: AssistantContext) -> tuple[Task, ...]:
        return tuple(self.resolver.resolve(context))

    def relevant(self, *, context: AssistantContext) -> list[Task]:
        return self.resolver.resolve(context)
