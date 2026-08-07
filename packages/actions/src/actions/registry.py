from __future__ import annotations

from actions.base import Action


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

    def clear(self) -> None:

        self._actions.clear()