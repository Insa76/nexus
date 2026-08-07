from __future__ import annotations

from core.connection_manager import ConnectionManager
from core.event_bus import EventBus
from core.event_queue import EventQueue
from core.runtime_state import RuntimeState


class Kernel:
    """
    Núcleo principal de NEXUS.

    El Kernel coordina los componentes fundamentales
    del sistema, pero no contiene lógica de negocio.

    Responsabilidades:

    - mantener el estado global
    - administrar conexiones
    - administrar eventos
    - exponer una única interfaz para el Runtime

    El Kernel NO conoce:

    - IA
    - Memoria
    - Planner
    - Knowledge
    - Providers
    - Agentes
    """

    def __init__(self) -> None:

        self.state = RuntimeState()

        self.connections = ConnectionManager()

        self.events = EventBus()

        self.queue = EventQueue()

    @property
    def online(self) -> bool:
        return self.state.online

    @property
    def connected_clients(self) -> int:
        return self.state.connected_clients

    def start(self) -> None:
        """
        Inicia el Kernel.
        """

        self.state.online = True

    def stop(self) -> None:
        """
        Detiene el Kernel.
        """

        self.state.online = False

    def info(self) -> dict:
        """
        Devuelve información básica del Kernel.
        """

        return {

            "online": self.state.online,

            "clients": self.state.connected_clients,

            "model": self.state.current_model,

            "version": self.state.kernel_version
        }