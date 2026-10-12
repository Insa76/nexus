from __future__ import annotations

import asyncio

from bootstrap.assistant_services import AssistantServices


class AssistantServicesLifecycle:
    """
    Controla el ciclo de vida de los servicios del Assistant Layer.

    El Scheduler se ejecuta como una tarea asyncio en background
    para no bloquear el proceso principal.
    """

    def __init__(
        self,
        services: AssistantServices,
    ) -> None:
        self.services = services
        self.running = False
        self._scheduler_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """
        Inicia los servicios del Assistant Layer.
        """

        if self.running:
            return

        self.running = True

        self._scheduler_task = asyncio.create_task(
            self.services.scheduler.start()
        )

    async def stop(self) -> None:
        """
        Detiene los servicios del Assistant Layer.
        """

        if not self.running:
            return

        self.running = False

        await self.services.scheduler.stop()

        if self._scheduler_task is not None:
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            finally:
                self._scheduler_task = None

    async def restart(self) -> None:
        """
        Reinicia los servicios del Assistant Layer.
        """

        await self.stop()
        await self.start()
