
from __future__ import annotations

import asyncio
import threading
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Awaitable, Callable


TaskCallback = Callable[[], Awaitable[None]]


@dataclass(slots=True)
class ScheduledTask:
    name: str
    interval: float
    callback: TaskCallback


@dataclass(slots=True)
class ScheduledOneShot:
    name: str
    execute_at: datetime
    callback: TaskCallback


class Scheduler:
    def __init__(self):
        self._tasks: list[ScheduledTask] = []
        self._one_shots: list[ScheduledOneShot] = []
        self._one_shot_tasks: dict[str, set[asyncio.Task[None]]] = {}
        self._periodic_tasks: set[asyncio.Task[None]] = set()
        self._running = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._stop_event: asyncio.Event | None = None
        self._state_lock = threading.RLock()

    def register(self, name, interval, callback):
        if interval <= 0:
            raise ValueError("interval must be greater than zero")

        with self._state_lock:
            self._tasks.append(
                ScheduledTask(
                    name=name,
                    interval=interval,
                    callback=callback,
                )
            )

    def register_at(self, name, execute_at, callback):
        one_shot = ScheduledOneShot(
            name=name,
            execute_at=execute_at,
            callback=callback,
        )

        with self._state_lock:
            self._one_shots.append(one_shot)
            loop = self._loop if self._running else None

        # Si el scheduler ya está activo, delegar la creación
        # de la tarea al hilo propietario del event loop.
        if loop is not None and not loop.is_closed():
            loop.call_soon_threadsafe(self._start_one_shot, one_shot)

    def cancel_one_shot(self, name):
        with self._state_lock:
            original_count = len(self._one_shots)
            self._one_shots = [
                item for item in self._one_shots
                if item.name != name
            ]
            found_pending = len(self._one_shots) < original_count
            loop = self._loop if self._running else None

        if loop is None or loop.is_closed():
            return found_pending

        # Si se llama desde el propio event loop, no bloquearlo.
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if current_loop is loop:
            return self._cancel_active_one_shot(name) or found_pending

        # Desde otro hilo, pedir la cancelación al event loop
        # y esperar su resultado para preservar el retorno bool.
        result: Future[bool] = Future()

        def cancel_on_loop():
            try:
                active = self._cancel_active_one_shot(name)
                result.set_result(active or found_pending)
            except Exception as exc:
                result.set_exception(exc)

        loop.call_soon_threadsafe(cancel_on_loop)
        return result.result(timeout=5)

    def _cancel_active_one_shot(self, name) -> bool:
        active_tasks = self._one_shot_tasks.pop(name, set())
        found_active = bool(active_tasks)

        for task in active_tasks:
            task.cancel()

        return found_active

    def _start_one_shot(self, one_shot):
        if self._loop is None:
            return

        if not self._running:
            return

        task = self._loop.create_task(self._run_one_shot(one_shot))
        self._one_shot_tasks.setdefault(one_shot.name, set()).add(task)
        return task

    async def start(self, *, keep_alive: bool = False) -> None:
        with self._state_lock:
            if self._running:
                return

            self._running = True
            self._loop = asyncio.get_running_loop()
            self._stop_event = asyncio.Event()
            initial_one_shots = list(self._one_shots)
            periodic_tasks = list(self._tasks)

        try:
            for scheduled in periodic_tasks:
                task = self._loop.create_task(self._run_task(scheduled))
                self._periodic_tasks.add(task)

            for one_shot in initial_one_shots:
                self._start_one_shot(one_shot)

            if keep_alive:
                assert self._stop_event is not None
                await self._stop_event.wait()
            elif self._periodic_tasks:
                await asyncio.gather(
                    *list(self._periodic_tasks),
                    return_exceptions=True,
                )
            else:
                while self._running:
                    active_tasks = {
                        task
                        for tasks in self._one_shot_tasks.values()
                        for task in tasks
                        if not task.done()
                    }

                    if not active_tasks:
                        break

                    await asyncio.gather(
                        *active_tasks,
                        return_exceptions=True,
                    )
        finally:
            with self._state_lock:
                self._running = False

            active_tasks = set(self._periodic_tasks)

            for tasks in self._one_shot_tasks.values():
                active_tasks.update(tasks)

            current = asyncio.current_task()
            if current is not None:
                active_tasks.discard(current)

            for task in active_tasks:
                if not task.done():
                    task.cancel()

            if active_tasks:
                await asyncio.gather(
                    *active_tasks,
                    return_exceptions=True,
                )

            self._periodic_tasks.difference_update(active_tasks)
            self._one_shot_tasks.clear()

            with self._state_lock:
                self._loop = None
                self._stop_event = None

    async def stop(self) -> None:
        with self._state_lock:
            self._running = False
            stop_event = self._stop_event

        if stop_event is not None:
            stop_event.set()

        active_tasks = set(self._periodic_tasks)

        for tasks in self._one_shot_tasks.values():
            active_tasks.update(tasks)

        current = asyncio.current_task()
        if current is not None:
            active_tasks.discard(current)

        for task in active_tasks:
            if not task.done():
                task.cancel()

        if active_tasks:
            await asyncio.gather(
                *active_tasks,
                return_exceptions=True,
            )

        self._periodic_tasks.difference_update(active_tasks)

    async def _run_task(self, task: ScheduledTask) -> None:
        try:
            while self._running:
                try:
                    await task.callback()
                except asyncio.CancelledError:
                    return
                except Exception as ex:
                    print(f"[Scheduler] {task.name}: {ex}")

                if self._running:
                    try:
                        await asyncio.sleep(task.interval)
                    except asyncio.CancelledError:
                        return
        finally:
            current = asyncio.current_task()
            if current is not None:
                self._periodic_tasks.discard(current)

    async def _run_one_shot(self, one_shot: ScheduledOneShot) -> None:
        try:
            now = datetime.now(timezone.utc)
            execute_at = one_shot.execute_at

            if execute_at.tzinfo is None:
                execute_at = execute_at.replace(tzinfo=timezone.utc)

            delay = (execute_at - now).total_seconds()

            if delay > 0:
                await asyncio.sleep(delay)

            if not self._running:
                return

            await one_shot.callback()

        except asyncio.CancelledError:
            return
        except Exception as ex:
            print(f"[Scheduler] {one_shot.name}: {ex}")
        finally:
            current = asyncio.current_task()
            active_tasks = self._one_shot_tasks.get(one_shot.name)

            if active_tasks is not None and current is not None:
                active_tasks.discard(current)

                if not active_tasks:
                    self._one_shot_tasks.pop(one_shot.name, None)

    def clear(self) -> None:
        with self._state_lock:
            self._tasks.clear()
            self._one_shots.clear()
            loop = self._loop if self._running else None

        def clear_active_tasks():
            for task in self._periodic_tasks:
                task.cancel()

            for active_tasks in self._one_shot_tasks.values():
                for task in active_tasks:
                    task.cancel()

            self._periodic_tasks.clear()
            self._one_shot_tasks.clear()

        if loop is not None and not loop.is_closed():
            try:
                current_loop = asyncio.get_running_loop()
            except RuntimeError:
                current_loop = None

            if current_loop is loop:
                clear_active_tasks()
            else:
                loop.call_soon_threadsafe(clear_active_tasks)
        else:
            clear_active_tasks()

    def tasks(self) -> list[str]:
        with self._state_lock:
            return [task.name for task in self._tasks]

    def one_shots(self) -> list[str]:
        with self._state_lock:
            return [one_shot.name for one_shot in self._one_shots]
