from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Any

from planner.intent import Intent


class IntentProvider(ABC):
    """
    Contrato para cualquier componente capaz
    de convertir texto del usuario en un Intent.
    """

    @abstractmethod
    async def recognize(
        self,
        text: str,
        capabilities: list[dict[str, Any]] | None = None,
        context: dict[str, Any] | None = None,
    ) -> Intent:
        """
        Convierte texto libre en un Intent.

        El contexto contiene información relevante
        de la WorkingMemory para resolver referencias
        y consultas contextuales.
        """
        ...
