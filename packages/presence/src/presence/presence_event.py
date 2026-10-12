from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class PresenceEvent:
    """
    Evento observable del estado de presencia de NEXUS.

    Este contrato representa lo que un consumidor externo
    puede conocer del estado cognitivo del runtime.

    No contiene chain-of-thought ni razonamiento privado.
    """

    state: str

    timestamp: datetime = field(
        default_factory=datetime.now,
    )

    message: str | None = None

    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "data": self.data,
        }
