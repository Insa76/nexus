from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Intent(BaseModel):
    """
    Representa una intención detectada
    a partir de una solicitud del usuario.
    """

    action: str

    confidence: float = 1.0

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )

    original_text: str