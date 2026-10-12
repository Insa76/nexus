from __future__ import annotations

from context import AssistantContext

from processes.models import Process
from processes.store import ProcessStore


class ProcessResolver:
    """Resolves processes relevant to an assistant context."""

    def __init__(self, store: ProcessStore) -> None:
        self._store = store

    def resolve(
        self,
        context: AssistantContext,
    ) -> list[Process]:
        processes = self._store.list()

        user = context.user
        organization = context.organization
        project_ids = {
            project.id
            for project in context.projects
        }

        resolved: list[Process] = []

        for process in processes:
            if user is not None and process.user_id == user.id:
                resolved.append(process)
                continue

            if (
                organization is not None
                and process.organization_id == organization.id
            ):
                resolved.append(process)
                continue

            if (
                process.project_id is not None
                and process.project_id in project_ids
            ):
                resolved.append(process)

        return resolved
