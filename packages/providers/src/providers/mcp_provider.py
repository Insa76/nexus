from __future__ import annotations

from typing import Any

from providers.provider import ToolProvider


class MCPProvider(ToolProvider):
    """
    Proveedor para herramientas expuestas
    mediante servidores MCP.
    """

    name = "mcp"

    async def execute(
        self,
        tool: str,
        parameters: dict[str, Any],
    ) -> Any:

        raise NotImplementedError(
            "MCP provider not implemented yet."
        )
