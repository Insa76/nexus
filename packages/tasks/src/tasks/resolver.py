from __future__ import annotations

from context import AssistantContext, project_ids_for_context
from tasks.models import Task
from tasks.store import TaskStore


class TaskResolver:
    """Resuelve tareas visibles para el usuario y proyecto activos."""

    def __init__(self, store: TaskStore) -> None:
        self._store = store

    def resolve(self, context: AssistantContext) -> list[Task]:
        user = context.user
        organization = context.organization
        project_ids = project_ids_for_context(context)
        resolved: list[Task] = []

        for task in self._store.list():
            # Un recurso asociado a un proyecto nunca debe filtrarse a través
            # de la coincidencia alternativa por usuario u organización.
            if task.project_id is not None and task.project_id not in project_ids:
                continue

            if user is not None and task.user_id == user.id:
                resolved.append(task)
                continue

            if organization is not None and task.organization_id == organization.id:
                resolved.append(task)
                continue

            if task.project_id is not None and task.project_id in project_ids:
                resolved.append(task)

        return resolved
