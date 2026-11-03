from __future__ import annotations

from context import AssistantContext, project_ids_for_context

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
        project_ids = project_ids_for_context(context)

        resolved: list[Process] = []

        for process in processes:
            # Los registros asociados a un proyecto solo son visibles
            # cuando ese proyecto pertenece al alcance activo.
            if process.project_id is not None:
                if process.project_id in project_ids:
                    resolved.append(process)
                continue

            if user is not None and process.user_id == user.id:
                resolved.append(process)
                continue

            if (
                organization is not None
                and process.organization_id == organization.id
            ):
                resolved.append(process)

        return resolved
