from __future__ import annotations

from collections.abc import Awaitable, Callable

from runtime.scheduler import Scheduler
from tasks import TemporalSchedule


TemporalCallback = Callable[[], Awaitable[None]]


class TemporalSchedulerAdapter:
    """
    Connects domain temporal schedules with the Runtime Scheduler.

    The adapter knows both sides of the boundary:
    - Assistant domain: TemporalSchedule
    - Runtime infrastructure: Scheduler

    Domain objects themselves remain unaware of Runtime.
    """

    def __init__(self, scheduler: Scheduler) -> None:
        self._scheduler = scheduler

    def schedule(
        self,
        temporal_schedule: TemporalSchedule,
        callback: TemporalCallback,
    ) -> None:
        self._scheduler.register_at(
            name=(
                f"{temporal_schedule.target_type}:"
                f"{temporal_schedule.target_id}"
            ),
            execute_at=temporal_schedule.execute_at,
            callback=callback,
        )

    def cancel(
        self,
        temporal_schedule: TemporalSchedule,
    ) -> bool:
        """
        Cancela una ejecución temporal previamente registrada.

        Devuelve True si la ejecución fue encontrada y cancelada.
        Devuelve False si no existía.
        """

        name = (
            f"{temporal_schedule.target_type}:"
            f"{temporal_schedule.target_id}"
        )

        return self._scheduler.cancel_one_shot(name)

    def scheduled(self) -> list[str]:
        return self._scheduler.one_shots()
