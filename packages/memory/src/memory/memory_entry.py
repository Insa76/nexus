from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """
    Representa un evento almacenado en la
    Working Memory de NEXUS.

    Una entrada puede representar una solicitud
    del usuario, una intención, una ejecución o
    un resultado.
    """

    id: str

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    type: str

    data: dict[str, Any] = Field(
        default_factory=dict
    )
