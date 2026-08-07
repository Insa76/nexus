from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable


TaskCallback = Callable[[], Awaitable[None]]


@dataclass(slots=True)
class ScheduledTask:
    """
    Representa una tarea periódica.
    """

    name: str
    interval: float
    callback: TaskCallback


class Scheduler:
    """
    Scheduler principal de NEXUS.

    Administra tareas periódicas.

    No conoce IA.
    No conoce Runtime.
    No conoce Providers.
    No conoce Planner.

    Solo ejecuta tareas registradas.
    """

    def __init__(self) -> None:

        self._tasks: list[ScheduledTask] = []

        self._running = False

    def register(
        self,
        name: str,
        interval: float,
        callback: TaskCallback,
    ) -> None:

        self._tasks.append(

            ScheduledTask(

                name=name,

                interval=interval,

                callback=callback,
            )
        )

    async def start(self) -> None:

        if self._running:
            return

        self._running = True

        await asyncio.gather(

            *[

                self._run_task(task)

                for task in self._tasks

            ]
        )

    async def stop(self) -> None:

        self._running = False

    async def _run_task(
        self,
        task: ScheduledTask,
    ) -> None:

        while self._running:

            try:

                await task.callback()

            except Exception as ex:

                print(

                    f"[Scheduler] {task.name}: {ex}"

                )

            await asyncio.sleep(

                task.interval

            )

    def clear(self) -> None:

        self._tasks.clear()

    def tasks(self) -> list[str]:

        return [

            task.name

            for task in self._tasks

        ]