from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any


EventHandler = Callable[[Any], Awaitable[None]]


class Dispatcher:
    """
    Despachador de eventos del Runtime.

    Su única responsabilidad es encontrar el
    handler registrado para un evento y ejecutarlo.

    No conoce IA.
    No conoce Planner.
    No conoce Memory.
    No conoce Providers.
    """

    def __init__(self) -> None:

        self._handlers: dict[str, EventHandler] = {}

    def register(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        """
        Registra un handler para un tipo de evento.
        """

        self._handlers[event_type] = handler

    def unregister(
        self,
        event_type: str,
    ) -> None:

        self._handlers.pop(
            event_type,
            None,
        )

    def has(
        self,
        event_type: str,
    ) -> bool:

        return event_type in self._handlers

    async def dispatch(
        self,
        event: Any,
    ) -> None:
        """
        Envía el evento al handler correspondiente.
        """

        handler = self._handlers.get(
            event.type
        )

        if handler is None:
            return

        await handler(event)

    def clear(self) -> None:

        self._handlers.clear()

    def handlers(self) -> list[str]:

        return sorted(
            self._handlers.keys()
        )