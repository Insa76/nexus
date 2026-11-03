from __future__ import annotations

from dataclasses import dataclass, replace

from context import AssistantContext, project_ids_for_context
from processes.models import Process, ProcessStatus
from processes.resolver import ProcessResolver
from processes.store import ProcessStore


@dataclass(slots=True)
class ProcessCapability:
    """Acceso a procesos limitado al contexto operativo activo."""

    store: ProcessStore
    resolver: ProcessResolver

    @staticmethod
    def _text(value: str, field: str, maximum: int, *, required: bool = True) -> str | None:
        if not isinstance(value, str):
            raise ValueError(f"El campo '{field}' debe ser texto.")
        cleaned = value.strip()
        if required and not cleaned:
            raise ValueError(f"El campo '{field}' es obligatorio.")
        if len(cleaned) > maximum:
            raise ValueError(f"El campo '{field}' supera {maximum} caracteres.")
        return cleaned or None

    def create(self, *, name: str, description: str | None = None,
               user_id: str | None = None, organization_id: str | None = None,
               project_id: str | None = None) -> Process:
        name = self._text(name, "name", 200)
        description = self._text(description, "description", 4000, required=False)
        return self.store.add(Process.create(
            name=name, description=description, user_id=user_id,
            organization_id=organization_id, project_id=project_id,
        ))

    def create_for_context(self, *, name: str, context: AssistantContext,
                           description: str | None = None) -> Process:
        active_project_id = context.metadata.get("active_project_id")
        allowed_projects = project_ids_for_context(context)
        if active_project_id is not None and active_project_id not in allowed_projects:
            raise ValueError("El proyecto activo no pertenece al contexto actual.")
        return self.create(
            name=name, description=description,
            user_id=context.user.id if context.user else None,
            organization_id=context.organization.id if context.organization else None,
            project_id=active_project_id,
        )

    def get(self, process_id: str) -> Process | None:
        return self.store.get(process_id)

    def list(self) -> list[Process]:
        return self.store.list()

    def relevant(self, *, context: AssistantContext) -> list[Process]:
        return self.resolver.resolve(context)

    def get_for_context(self, process_id: str, *, context: AssistantContext) -> Process | None:
        visible = self.relevant(context=context)
        by_id = next((item for item in visible if item.id == process_id), None)
        if by_id is not None:
            return by_id
        normalized = process_id.strip().casefold()
        matches = [item for item in visible if item.name.strip().casefold() == normalized]
        return matches[0] if normalized and len(matches) == 1 else None

    def update_for_context(self, process_id: str, *, context: AssistantContext,
                           name: str | None = None, description: str | None = None) -> Process | None:
        process = self.get_for_context(process_id, context=context)
        if process is None:
            return None
        changes = {}
        if name is not None:
            changes["name"] = self._text(name, "name", 200)
        if description is not None:
            changes["description"] = self._text(description, "description", 4000, required=False)
        if not changes:
            raise ValueError("No se indicó ningún campo para actualizar.")
        return self.store.update(replace(process, **changes))

    def transition_for_context(self, process_id: str, target: ProcessStatus,
                               *, context: AssistantContext) -> Process | None:
        process = self.get_for_context(process_id, context=context)
        if process is None:
            return None
        allowed = {
            ProcessStatus.PENDING: {ProcessStatus.IN_PROGRESS, ProcessStatus.CANCELLED},
            ProcessStatus.IN_PROGRESS: {ProcessStatus.COMPLETED, ProcessStatus.CANCELLED},
            ProcessStatus.COMPLETED: set(),
            ProcessStatus.CANCELLED: set(),
        }
        if target not in allowed[process.status]:
            raise ValueError(f"Transición de proceso no permitida: {process.status.value} -> {target.value}.")
        return self.store.update(replace(process, status=target))

    def update(self, process: Process) -> Process:
        return self.store.update(process)

    def remove(self, process_id: str) -> Process | None:
        return self.store.remove(process_id)
