from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import replace
from datetime import datetime

from tasks import (
    Reminder,
    ReminderStatus,
    ReminderStore,
    ReminderTriggerHandler,
    ReminderTriggerResult,
    reminder_to_schedule,
    transition_reminder,
)

from bootstrap.temporal_scheduler import TemporalSchedulerAdapter


TriggerCallback = Callable[[ReminderTriggerResult], Awaitable[None]]


class ReminderScheduler:
    """
    Composition layer for end-to-end reminder scheduling.

    Responsibilities:
    - Convert a Reminder into a TemporalSchedule.
    - Register the schedule through TemporalSchedulerAdapter.
    - Trigger the reminder when its scheduled time arrives.
    - Persist the resulting triggered Reminder.
    - Optionally notify an external async callback.

    The Reminder domain remains independent from the Scheduler.
    """

    def __init__(
        self,
        scheduler_adapter: TemporalSchedulerAdapter,
        reminder_store: ReminderStore,
        trigger_handler: ReminderTriggerHandler | None = None,
    ) -> None:
        self._scheduler_adapter = scheduler_adapter
        self._reminder_store = reminder_store
        self._trigger_handler = trigger_handler or ReminderTriggerHandler()

    def schedule(
        self,
        reminder: Reminder,
        on_trigger: TriggerCallback | None = None,
    ) -> None:
        """
        Schedule a pending reminder for future execution.
        """

        temporal_schedule = reminder_to_schedule(reminder)

        async def handle_trigger() -> None:
            result = self._trigger_handler.handle(reminder)

            self._reminder_store.update(result.reminder)

            if on_trigger is not None:
                await on_trigger(result)

        self._scheduler_adapter.schedule(
            temporal_schedule=temporal_schedule,
            callback=handle_trigger,
        )

    def cancel(
        self,
        reminder_id: str,
    ) -> bool:
        """
        Cancela un reminder pendiente y elimina su ejecución temporal.

        Devuelve True si el reminder fue cancelado.
        Devuelve False si no existe.
        """

        reminder = self._reminder_store.get(reminder_id)

        if reminder is None:
            return False

        cancelled = transition_reminder(
            reminder,
            ReminderStatus.CANCELLED,
        )

        temporal_schedule = reminder_to_schedule(
            reminder,
        )

        scheduler_cancelled = self._scheduler_adapter.cancel(
            temporal_schedule,
        )

        self._reminder_store.update(cancelled)

        return scheduler_cancelled

    def reschedule(
        self,
        reminder_id: str,
        trigger_at: datetime,
    ) -> bool:
        """
        Cambia la fecha de ejecución de un reminder pendiente.

        Elimina la ejecución temporal anterior, actualiza el reminder
        y registra una nueva ejecución temporal.

        Devuelve True si el reminder fue reprogramado.
        Devuelve False si no existe.
        """

        reminder = self._reminder_store.get(reminder_id)

        if reminder is None:
            return False

        if reminder.status is not ReminderStatus.PENDING:
            return False

        current_schedule = reminder_to_schedule(
            reminder,
        )

        self._scheduler_adapter.cancel(
            current_schedule,
        )

        updated_reminder = replace(
            reminder,
            trigger_at=trigger_at,
        )

        self._reminder_store.update(
            updated_reminder,
        )

        self.schedule(
            updated_reminder,
        )

        return True

    def reconcile(self) -> int:
        """
        Reconstruye las ejecuciones temporales de todos los reminders
        pendientes actualmente almacenados.

        Devuelve la cantidad de reminders programados.
        """

        scheduled_count = 0

        for reminder in self._reminder_store.list():
            if reminder.status is not ReminderStatus.PENDING:
                continue

            schedule = reminder_to_schedule(reminder)

            schedule_name = (
                f"{schedule.target_type}:"
                f"{schedule.target_id}"
            )

            if schedule_name in self._scheduler_adapter.scheduled():
                continue

            self.schedule(reminder)
            scheduled_count += 1

        return scheduled_count

    def get(self, reminder_id: str) -> Reminder | None:
        """
        Return the current persisted state of a reminder.
        """

        return self._reminder_store.get(reminder_id)
