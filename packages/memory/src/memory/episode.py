from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Episode(BaseModel):
    """
    Representa una experiencia completa de NEXUS.

    Un episodio describe qué solicitó el usuario,
    qué acción fue ejecutada y cuál fue su resultado.

    No ejecuta acciones.
    No interpreta intenciones.
    No consulta memoria.
    """

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    action: str

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )

    original_text: str = ""

    success: bool = True

    output: Any = None
