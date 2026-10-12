from __future__ import annotations

from collections.abc import Callable
from threading import RLock
from typing import Any

from .presence_event import PresenceEvent


PresenceListener = Callable[[PresenceEvent], None]


class PresenceEventBus:
    """
    Bus de eventos observables de NEXUS.

    Permite que consumidores externos como:
    - NEXUS Console
    - JARVIS
    - futuras interfaces

    reciban transiciones reales del runtime.

    El bus no contiene lógica cognitiva.
    No ejecuta acciones.
    No modifica el Engine.

    Los listeners reciben solamente información
    observable y estructurada.
    """

    def __init__(self) -> None:
        self._listeners: set[PresenceListener] = set()
        self._lock = RLock()

    def subscribe(
        self,
        listener: PresenceListener,
    ) -> Callable[[], None]:
        """
        Registra un listener y devuelve una función
        para cancelar la suscripción.
        """

        with self._lock:
            self._listeners.add(listener)

        def unsubscribe() -> None:
            with self._lock:
                self._listeners.discard(listener)

        return unsubscribe

    def emit(
        self,
        event: PresenceEvent,
    ) -> None:
        """
        Publica un evento a todos los listeners actuales.

        Un error de un consumidor no debe romper NEXUS.
        """

        with self._lock:
            listeners = tuple(self._listeners)

        for listener in listeners:
            try:
                listener(event)
            except Exception:
                continue

    def emit_state(
        self,
        state: str,
        *,
        message: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> PresenceEvent:
        """
        Crea y publica un PresenceEvent.
        """

        event = PresenceEvent(
            state=state,
            message=message,
            data=data,
        )

        self.emit(event)

        return event
