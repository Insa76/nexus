from __future__ import annotations

from actions.base import Action
from providers.tool import Tool


class ActionRegistry:
    """
    Registro de Actions disponibles.
    """

    def __init__(self) -> None:

        self._actions: dict[str, Action] = {}

    def register(
        self,
        action: Action,
    ) -> None:

        self._actions[action.name] = action

    def unregister(
        self,
        name: str,
    ) -> None:

        self._actions.pop(
            name,
            None,
        )

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._actions

    def get(
        self,
        name: str,
    ) -> Action:

        if name not in self._actions:

            raise KeyError(
                f"Action '{name}' not registered."
            )

        return self._actions[name]

    def list(self) -> list[str]:

        return sorted(
            self._actions.keys()
        )

    def describe(self) -> list[Tool]:
        """
        Devuelve una descripción de las Actions
        internas de NEXUS.

        La descripción incluye los artifacts que
        cada Action consume y produce.
        """

        tools: list[Tool] = []

        for action in self._actions.values():

            if not action.internal:
                continue

            description = (
                action.description
                if action.description
                else (
                    f"Capacidad interna: "
                    f"{action.name}"
                )
            )

            tools.append(
                Tool(
                    name=f"nexus.{action.name}",
                    description=description,
                    provider="nexus",
                    action=action.name,
                    parameters=dict(
                        action.parameters
                    ),
                    produces=list(
                        action.produces
                    ),
                    consumes=list(
                        action.consumes
                    ),
                )
            )

        return sorted(
            tools,
            key=lambda tool: tool.name,
        )

    def clear(self) -> None:

        self._actions.clear()
