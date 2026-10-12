from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
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


@dataclass(slots=True)
class ScheduledOneShot:
    """
    Representa una ejecución única en un instante absoluto.
    """

    name: str
    execute_at: datetime
    callback: TaskCallback


class Scheduler:
    """
    Scheduler principal de NEXUS.

    Administra tareas periódicas y ejecuciones únicas.

    No conoce IA.
    No conoce Providers.
    No conoce Planner.

    Solo ejecuta tareas registradas.
    """

    def __init__(self) -> None:
        self._tasks: list[ScheduledTask] = []
        self._one_shots: list[ScheduledOneShot] = []
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

    def register_at(
        self,
        name: str,
        execute_at: datetime,
        callback: TaskCallback,
    ) -> None:
        self._one_shots.append(
            ScheduledOneShot(
                name=name,
                execute_at=execute_at,
                callback=callback,
            )
        )

    def cancel_one_shot(
        self,
        name: str,
    ) -> bool:
        """
        Cancela una ejecución única previamente registrada.

        Devuelve True si se encontró y eliminó la ejecución.
        Devuelve False si no existía una ejecución con ese nombre.
        """

        original_count = len(self._one_shots)

        self._one_shots = [
            one_shot
            for one_shot in self._one_shots
            if one_shot.name != name
        ]

        return len(self._one_shots) < original_count

    async def start(self) -> None:
        if self._running:
            return

        self._running = True

        await asyncio.gather(
            *[
                self._run_task(task)
                for task in self._tasks
            ],
            *[
                self._run_one_shot(one_shot)
                for one_shot in self._one_shots
            ],
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

    async def _run_one_shot(
        self,
        one_shot: ScheduledOneShot,
    ) -> None:
        try:
            now = datetime.now(timezone.utc)

            execute_at = one_shot.execute_at

            if execute_at.tzinfo is None:
                execute_at = execute_at.replace(
                    tzinfo=timezone.utc
                )

            delay = (
                execute_at - now
            ).total_seconds()

            if delay > 0:
                await asyncio.sleep(delay)

            if not self._running:
                return

            await one_shot.callback()

        except Exception as ex:
            print(
                f"[Scheduler] {one_shot.name}: {ex}"
            )

    def clear(self) -> None:
        self._tasks.clear()
        self._one_shots.clear()

    def tasks(self) -> list[str]:
        return [
            task.name
            for task in self._tasks
        ]

    def one_shots(self) -> list[str]:
        return [
            one_shot.name
            for one_shot in self._one_shots
        ]
