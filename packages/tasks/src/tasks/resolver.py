from __future__ import annotations

from context import AssistantContext, project_ids_for_context, project_ids_for_context

from tasks.models import Task
from tasks.store import TaskStore


class TaskResolver:
    """Resolves tasks relevant to an assistant context."""

    def __init__(self, store: TaskStore) -> None:
        self._store = store

    def resolve(self, context: AssistantContext) -> list[Task]:
        tasks = self._store.list()

        user = context.user
        organization = context.organization
        project_ids = project_ids_for_context(context)

        resolved: list[Task] = []

        for task in tasks:
            if user is not None and task.user_id == user.id:
                resolved.append(task)
                continue

            if (
                organization is not None
                and task.organization_id == organization.id
            ):
                resolved.append(task)
                continue

            if task.project_id is not None and task.project_id in project_ids:
                resolved.append(task)

        return resolved
