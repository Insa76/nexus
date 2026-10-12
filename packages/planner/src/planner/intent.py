from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Intent(BaseModel):
    """
    Representa una intención detectada
    a partir de una solicitud del usuario.

    Una Intent puede representar:

    - una acción simple
    - una secuencia de sub-intenciones

    Las intenciones simples mantienen exactamente
    el comportamiento anterior.
    """

    action: str

    confidence: float = 1.0

    parameters: dict[str, Any] = Field(
        default_factory=dict
    )

    original_text: str

    sub_intents: list["Intent"] = Field(
        default_factory=list
    )

    @property
    def is_compound(self) -> bool:
        """
        Indica si la intención contiene
        múltiples intenciones ejecutables.
        """

        return len(self.sub_intents) > 0
