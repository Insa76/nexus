from __future__ import annotations

from providers.tool import Tool


class ToolRegistry:
    """
    Registro central de herramientas disponibles
    para NEXUS.

    El Registry describe las herramientas.
    No ejecuta herramientas.
    """

    def __init__(self) -> None:

        self._tools: dict[str, Tool] = {}

    def register(
        self,
        tool: Tool,
    ) -> None:

        self._tools[tool.name] = tool

    def register_many(
        self,
        tools: list[Tool],
    ) -> None:

        for tool in tools:

            self.register(
                tool
            )

    def unregister(
        self,
        name: str,
    ) -> None:

        self._tools.pop(
            name,
            None,
        )

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._tools

    def get(
        self,
        name: str,
    ) -> Tool:

        if name not in self._tools:

            raise KeyError(
                f"Tool '{name}' not registered."
            )

        return self._tools[name]

    def find_by_action(
        self,
        action: str,
    ) -> Tool | None:
        """
        Busca la herramienta asociada
        a una Action.
        """

        for tool in self._tools.values():

            if tool.action == action:

                return tool

        return None

    def resolve(
        self,
        action: str,
    ) -> Tool | None:
        """
        Resuelve una Action contra la herramienta
        registrada que la implementa.

        El Planner utiliza este método para comprobar
        que una intención pueda convertirse en un plan.

        El Registry solamente resuelve capacidades.
        No ejecuta herramientas.
        """

        return self.find_by_action(
            action
        )

    def list(self) -> list[str]:

        return sorted(
            self._tools.keys()
        )

    def all(self) -> list[Tool]:

        return list(
            self._tools.values()
        )

    def describe(self) -> list[dict]:
        """
        Devuelve una descripción serializable
        de todas las capacidades disponibles
        para NEXUS.
        """

        capabilities = []

        for tool in self._tools.values():

            capabilities.append(
                {
                    "name": tool.name,
                    "action": tool.action,
                    "description": tool.description,
                    "provider": tool.provider,
                    "parameters": tool.parameters,
                }
            )

        return sorted(
            capabilities,
            key=lambda item: item["name"],
        )

    def clear(self) -> None:

        self._tools.clear()
