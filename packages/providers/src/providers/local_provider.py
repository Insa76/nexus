from __future__ import annotations

from typing import Any

from adapters.windows.app_launcher import (
    WindowsAppLauncher,
)

from adapters.windows.process_manager import (
    WindowsProcessManager,
)

from adapters.windows.screen_capture import (
    WindowsScreenCapture,
)

from adapters.windows.volume_control import (
    WindowsVolumeControl,
)

from providers.provider import ToolProvider
from providers.tool import Tool


class LocalProvider(ToolProvider):
    """
    Proveedor local de NEXUS.

    Utiliza exclusivamente adapters del sistema operativo
    para ejecutar herramientas locales.

    El LocalProvider no conoce Actions y nunca debe
    invocar Action.execute() ni Action.execute_local().

    Flujo:

        Action
            ↓
        ProviderManager
            ↓
        LocalProvider
            ↓
        Windows Adapter
    """

    name = "local"

    def __init__(self) -> None:

        self._launcher = WindowsAppLauncher()

        self._process_manager = (
            WindowsProcessManager()
        )

        self._screen_capture = (
            WindowsScreenCapture()
        )

        self._volume_control = (
            WindowsVolumeControl()
        )

    def tools(self) -> list[Tool]:
        """
        Devuelve las herramientas disponibles
        en el proveedor local.
        """

        return [
            Tool(
                name="windows.open_app",
                action="system.open_app",
                description="Abre una aplicación de Windows.",
                provider=self.name,
                parameters={
                    "application": {
                        "type": "string",
                        "required": True,
                        "description": (
                            "Nombre de la aplicación."
                        ),
                    },
                },
            ),

            Tool(
                name="windows.list_processes",
                action="system.process_list",
                description=(
                    "Obtiene los procesos activos de Windows."
                ),
                provider=self.name,
                parameters={},
            ),

            Tool(
                name="windows.close_app",
                action="system.close_app",
                description=(
                    "Cierra una aplicación en ejecución."
                ),
                provider=self.name,
                parameters={
                    "application": {
                        "type": "string",
                        "required": True,
                        "description": (
                            "Nombre de la aplicación."
                        ),
                    },
                },
            ),

            Tool(
                name="windows.capture_screen",
                action="system.screen_capture",
                description="Captura la pantalla actual.",
                provider=self.name,
                parameters={},
                produces=[
                    "image",
                ],
            ),

            Tool(
                name="windows.set_volume",
                action="system.set_volume",
                description=(
                    "Establece el volumen maestro de Windows."
                ),
                provider=self.name,
                parameters={
                    "level": {
                        "type": "number",
                        "required": True,
                        "description": (
                            "Volumen entre 0 y 100."
                        ),
                    },
                },
            ),

            Tool(
                name="windows.get_volume",
                action="system.get_volume",
                description=(
                    "Obtiene el volumen actual de Windows."
                ),
                provider=self.name,
                parameters={},
            ),

            Tool(
                name="windows.mute",
                action="system.mute",
                description=(
                    "Silencia el volumen de Windows."
                ),
                provider=self.name,
                parameters={},
            ),

            Tool(
                name="windows.unmute",
                action="system.unmute",
                description=(
                    "Quita el silencio de Windows."
                ),
                provider=self.name,
                parameters={},
            ),

            Tool(
                name="windows.get_mute",
                action="system.get_mute",
                description=(
                    "Obtiene el estado actual de silencio "
                    "de Windows."
                ),
                provider=self.name,
                parameters={},
            ),
        ]

    async def execute(
        self,
        tool: str,
        parameters: dict[str, Any],
    ) -> Any:

        if tool == "windows.open_app":
            return await self._open_app(
                parameters
            )

        if tool == "windows.list_processes":
            return await self._list_processes()

        if tool == "windows.close_app":
            return await self._close_app(
                parameters
            )

        if tool == "windows.capture_screen":
            return await self._capture_screen()

        if tool == "windows.set_volume":
            return await self._set_volume(
                parameters
            )

        if tool == "windows.get_volume":
            return await self._get_volume()

        if tool == "windows.mute":
            return await self._mute()

        if tool == "windows.unmute":
            return await self._unmute()

        if tool == "windows.get_mute":
            return await self._get_mute()

        raise KeyError(
            f"Tool '{tool}' not available "
            f"in provider '{self.name}'."
        )

    async def _open_app(
        self,
        parameters: dict[str, Any],
    ) -> Any:

        application = parameters.get(
            "application"
        )

        if not application:
            return False

        return self._launcher.open(
            application
        )

    async def _list_processes(self) -> Any:

        return self._process_manager.list()

    async def _close_app(
        self,
        parameters: dict[str, Any],
    ) -> Any:

        application = parameters.get(
            "application"
        )

        if not application:
            return False

        return self._process_manager.close(
            application
        )

    async def _capture_screen(self) -> Any:

        return self._screen_capture.capture()

    async def _set_volume(
        self,
        parameters: dict[str, Any],
    ) -> Any:

        level = parameters.get("level")

        if level is None:
            return False

        return self._volume_control.set(
            float(level)
        )

    async def _get_volume(self) -> Any:

        return self._volume_control.get()

    async def _mute(self) -> Any:

        return self._volume_control.mute()

    async def _unmute(self) -> Any:

        return self._volume_control.unmute()

    async def _get_mute(self) -> Any:

        return self._volume_control.is_muted()
