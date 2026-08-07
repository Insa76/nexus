from __future__ import annotations

from typing import Any


class Registry:
    """
    Registro de módulos del Runtime.

    Mantiene un catálogo de todos los módulos
    cargados en el sistema.

    No crea módulos.
    No ejecuta módulos.
    No conoce implementaciones.
    """

    def __init__(self) -> None:

        self._modules: dict[str, Any] = {}

    def register(
        self,
        name: str,
        module: Any,
    ) -> None:
        """
        Registra un módulo.
        """

        self._modules[name] = module

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Devuelve un módulo registrado.
        """

        if name not in self._modules:

            raise KeyError(
                f"Module '{name}' not registered."
            )

        return self._modules[name]

    def has(
        self,
        name: str,
    ) -> bool:

        return name in self._modules

    def unregister(
        self,
        name: str,
    ) -> None:

        self._modules.pop(
            name,
            None,
        )

    def clear(self) -> None:

        self._modules.clear()

    def modules(self) -> list[str]:

        return sorted(
            self._modules.keys()
        )