import asyncio
from typing import Any


class EventQueue:
    """
    Cola de eventos del Kernel.

    Centraliza el ingreso de eventos que luego serán
    procesados por el Runtime.

    La cola es completamente asíncrona y mantiene
    prioridad por evento.
    """

    def __init__(self):

        self._queue: asyncio.PriorityQueue[
            tuple[int, Any]
        ] = asyncio.PriorityQueue()

    async def put(
        self,
        priority: int,
        event: Any
    ) -> None:

        """
        Agrega un evento a la cola.

        A mayor prioridad, antes será procesado.
        """

        await self._queue.put(
            (-priority, event)
        )

    async def get(self) -> Any:

        """
        Espera hasta que exista un evento disponible.
        """

        _, event = await self._queue.get()

        return event

    def empty(self) -> bool:

        return self._queue.empty()

    def size(self) -> int:

        return self._queue.qsize()