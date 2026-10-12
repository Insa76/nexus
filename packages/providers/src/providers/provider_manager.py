from __future__ import annotations

from typing import Any

from providers.provider import ToolProvider
from providers.tool import Tool


class ProviderManager:
    """
    Administra todos los proveedores registrados.

    Es el único componente que sabe qué proveedor
    puede ejecutar una herramienta determinada.
    """

    def __init__(self) -> None:

        self._providers: dict[str, ToolProvider] = {}

    def register(
        self,
        provider: ToolProvider,
    ) -> None:

        self._providers[
            provider.name
        ] = provider

    def unregister(
        self,
        name: str,
    ) -> None:

        self._providers.pop(
            name,
            None,
        )

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._providers

    def get(
        self,
        name: str,
    ) -> ToolProvider:

        if name not in self._providers:

            raise KeyError(
                f"Provider '{name}' not registered."
            )

        return self._providers[name]

    async def execute(
        self,
        provider: str,
        tool: str,
        parameters: dict[str, Any],
    ) -> Any:

        selected_provider = self.get(
            provider
        )

        return await selected_provider.execute(
            tool,
            parameters,
        )

    def tools(self) -> list[Tool]:
        """
        Devuelve todas las herramientas disponibles
        en todos los proveedores registrados.
        """

        tools: list[Tool] = []

        for provider in self._providers.values():

            provider_tools = getattr(
                provider,
                "tools",
                None,
            )

            if provider_tools is None:
                continue

            tools.extend(
                provider_tools()
            )

        return tools

    def list_tools(self) -> list[str]:
        """
        Devuelve los nombres de todas las herramientas
        disponibles.
        """

        return sorted(
            tool.name
            for tool in self.tools()
        )

    def list(self) -> list[str]:

        return sorted(
            self._providers.keys()
        )
