from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from processes.capability import ProcessCapability
from processes.models import Process


@dataclass(frozen=True, slots=True)
class ProcessCognitiveResult:
    """
    Resultado de una operación cognitiva sobre Processes.

    Expone información que el Cognitive Core puede utilizar
    sin conocer stores ni detalles internos del subsistema.
    """

    processes: tuple[Process, ...]
    metadata: dict[str, Any]


class ProcessCognitiveAccess:
    """
    Punto de acceso cognitivo a Processes.

    Traduce una necesidad cognitiva del Assistant
    en una operación sobre ProcessCapability.
    """

    def __init__(
        self,
        capability: ProcessCapability,
    ) -> None:
        self._capability = capability

    def find_relevant(
        self,
        *,
        context: object,
    ) -> ProcessCognitiveResult:
        processes = self._capability.relevant(
            context=context,
        )

        return ProcessCognitiveResult(
            processes=tuple(processes),
            metadata={
                "operation": "processes.find_relevant",
                "count": len(processes),
            },
        )

    def get(
        self,
        process_id: str,
    ) -> Process | None:
        return self._capability.get(process_id)

    def list(self) -> tuple[Process, ...]:
        return tuple(self._capability.list())
