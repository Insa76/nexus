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
        *,
        context: object,
    ) -> Process | None:
        processes = self._capability.relevant(
            context=context,
        )

        return next(
            (
                process
                for process in processes
                if process.id == process_id
            ),
            None,
        )

    def list(
        self,
        *,
        context: object,
    ) -> tuple[Process, ...]:
        return tuple(
            self._capability.relevant(
                context=context,
            )
        )
