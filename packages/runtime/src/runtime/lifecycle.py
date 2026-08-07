from __future__ import annotations

from packages.runtime.src.runtime.runtime import Runtime


class Lifecycle:
    """
    Controla el ciclo de vida del Runtime.

    Este componente únicamente administra el
    inicio y la detención del sistema.
    """

    def __init__(self, runtime: Runtime) -> None:

        self.runtime = runtime

        self.running = False

    async def start(self) -> None:
        """
        Inicia el Runtime.
        """

        if self.running:
            return

        self.running = True

        self.runtime.kernel.start()

    async def stop(self) -> None:
        """
        Detiene el Runtime.
        """

        if not self.running:
            return

        self.running = False

        self.runtime.kernel.stop()

    async def restart(self) -> None:
        """
        Reinicia el Runtime.
        """

        await self.stop()

        await self.start()