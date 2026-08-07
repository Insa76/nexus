from __future__ import annotations

from collections import deque
from typing import Any


class EventBus:
    """
    Bus interno de eventos del Kernel.

    Su única responsabilidad es almacenar eventos
    publicados por distintos componentes y entregarlos
    posteriormente para su procesamiento.

    No conoce WebSocket.
    No conoce IA.
    No conoce Runtime.
    """

    def __init__(self) -> None:
        self._events: deque[Any] = deque()

    def emit(self, event: Any) -> None:
        """
        Publica un nuevo evento.
        """
        self._events.append(event)

    def consume_all(self) -> list[Any]:
        """
        Devuelve todos los eventos pendientes y limpia el bus.
        """

        events = list(self._events)

        self._events.clear()

        return events

    def has_events(self) -> bool:
        """
        Indica si existen eventos pendientes.
        """

        return len(self._events) > 0

    def size(self) -> int:
        """
        Cantidad de eventos pendientes.
        """

        return len(self._events)

    def clear(self) -> None:
        """
        Elimina todos los eventos pendientes.
        """

        self._events.clear()