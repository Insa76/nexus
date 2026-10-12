from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ToolProvider(ABC):
    """
    Contrato base para cualquier proveedor de herramientas.

    Un proveedor puede ser:

    - MCP
    - Windows Local
    - Linux
    - Cloud
    """

    name: str

    @abstractmethod
    async def execute(
        self,
        tool: str,
        parameters: dict[str, Any],
    ) -> Any:
        ...
