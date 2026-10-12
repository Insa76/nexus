from __future__ import annotations

from dataclasses import dataclass

from context import AssistantContext

from processes.models import Process
from processes.resolver import ProcessResolver
from processes.store import ProcessStore


@dataclass(slots=True)
class ProcessCapability:
    """
    Interfaz cognitiva de acceso a procesos.

    Expone operaciones orientadas al Assistant/Cognitive Core
    sin exponer directamente stores ni detalles internos.
    """

    store: ProcessStore
    resolver: ProcessResolver

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> Process:
        process = Process.create(
            name=name,
            description=description,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )

        return self.store.add(process)

    def get(
        self,
        process_id: str,
    ) -> Process | None:
        return self.store.get(process_id)

    def list(
        self,
    ) -> list[Process]:
        return self.store.list()

    def relevant(
        self,
        *,
        context: AssistantContext,
    ) -> list[Process]:
        return self.resolver.resolve(context)

    def update(
        self,
        process: Process,
    ) -> Process:
        return self.store.update(process)

    def remove(
        self,
        process_id: str,
    ) -> Process | None:
        return self.store.remove(process_id)
