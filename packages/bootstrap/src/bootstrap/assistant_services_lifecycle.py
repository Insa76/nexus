
from __future__ import annotations

import asyncio

from bootstrap.assistant_services import AssistantServices


class AssistantServicesLifecycle:
    """
    Controls the lifecycle of Assistant Layer services.
    """

    def __init__(self, services: AssistantServices) -> None:
        self.services = services
        self.running = False
        self._scheduler_task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Restore pending reminder schedules and start the scheduler."""

        if self.running:
            return

        self.services.reminder_scheduler.reconcile()

        self.running = True

        try:
            self._scheduler_task = asyncio.create_task(
                self.services.scheduler.start()
            )
        except Exception:
            self.running = False
            raise

    async def stop(self) -> None:
        """Stop the background scheduler."""

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
        """Restart the services."""

        await self.stop()
        await self.start()
