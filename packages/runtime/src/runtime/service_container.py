from __future__ import annotations

from typing import Any


class ServiceContainer:
    """
    Contenedor de dependencias del Runtime.

    Es el único responsable de almacenar y entregar
    servicios compartidos entre los distintos módulos.

    No crea objetos.
    No conoce implementaciones.
    No contiene lógica de negocio.
    """

    def __init__(self) -> None:

        self._services: dict[str, Any] = {}

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Registra un servicio.
        """

        self._services[name] = service

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Obtiene un servicio previamente registrado.
        """

        if name not in self._services:

            raise KeyError(
                f"Service '{name}' not registered."
            )

        return self._services[name]

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._services

    def remove(
        self,
        name: str,
    ) -> None:

        self._services.pop(
            name,
            None,
        )

    def clear(self) -> None:

        self._services.clear()

    def services(self) -> list[str]:

        return sorted(
            self._services.keys()
        )