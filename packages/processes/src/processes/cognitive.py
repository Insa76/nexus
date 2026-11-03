from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from processes.capability import ProcessCapability
from processes.models import Process, ProcessStatus


@dataclass(frozen=True, slots=True)
class ProcessCognitiveResult:
    processes: tuple[Process, ...]
    metadata: dict[str, Any]


class ProcessCognitiveAccess:
    """Traduce operaciones cognitivas al subsistema Processes."""

    def __init__(self, capability: ProcessCapability) -> None:
        self._capability = capability

    def find_relevant(self, *, context: object) -> ProcessCognitiveResult:
        processes = self._capability.relevant(context=context)
        return ProcessCognitiveResult(
            processes=tuple(processes),
            metadata={"operation": "processes.find_relevant", "count": len(processes)},
        )

    def get(self, process_id: str, *, context: object) -> Process | None:
        return self._capability.get_for_context(process_id, context=context)

    def list(self, *, context: object) -> tuple[Process, ...]:
        return tuple(self._capability.relevant(context=context))

    def create(self, *, context: object, name: str, description: str | None = None) -> Process:
        return self._capability.create_for_context(name=name, description=description, context=context)

    def update(self, process_id: str, *, context: object,
               name: str | None = None, description: str | None = None) -> Process | None:
        return self._capability.update_for_context(
            process_id, context=context, name=name, description=description,
        )

    def transition(self, process_id: str, target_status: ProcessStatus,
                   *, context: object) -> Process | None:
        return self._capability.transition_for_context(
            process_id, target_status, context=context,
        )
