from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from bootstrap.reminder_scheduler import ReminderScheduler
from bootstrap.temporal_scheduler import TemporalSchedulerAdapter
from runtime.scheduler import Scheduler
from tasks import Reminder, ReminderStatus, ReminderStore


def test_schedule_registers_one_shot() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Revisar el informe",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    store.add(reminder)
    reminder_scheduler.schedule(reminder)

    assert scheduler.one_shots() == [
        f"reminder:{reminder.id}",
    ]


def test_schedule_rejects_non_pending_reminder() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Recordatorio cancelado",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    cancelled = reminder.__class__(
        **{
            **reminder.__dict__,
            "status": ReminderStatus.CANCELLED,
        }
    )

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    try:
        reminder_scheduler.schedule(cancelled)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_trigger_updates_store() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Revisar el informe",
        trigger_at=datetime.now(timezone.utc),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.schedule(reminder)

    async def run() -> None:
        await scheduler.start()

    asyncio.run(run())

    stored = reminder_scheduler.get(reminder.id)

    assert stored is not None
    assert stored.status is ReminderStatus.TRIGGERED


def test_trigger_callback_receives_result() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Llamar al cliente",
        trigger_at=datetime.now(timezone.utc),
    )

    store.add(reminder)

    received = []

    async def on_trigger(result) -> None:
        received.append(result)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.schedule(
        reminder,
        on_trigger=on_trigger,
    )

    async def run() -> None:
        await scheduler.start()

    asyncio.run(run())

    assert len(received) == 1
    assert received[0].reminder_id == reminder.id
    assert received[0].message == "Llamar al cliente"
    assert received[0].reminder.status is ReminderStatus.TRIGGERED


def test_get_returns_current_reminder_state() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Enviar propuesta",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    result = reminder_scheduler.get(reminder.id)

    assert result == reminder

def test_cancel_reminder_updates_store_and_removes_schedule() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Cancelar esta tarea",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.schedule(reminder)

    assert scheduler.one_shots() == [
        f"reminder:{reminder.id}",
    ]

    cancelled = reminder_scheduler.cancel(reminder.id)

    assert cancelled is True
    assert scheduler.one_shots() == []

    stored = reminder_scheduler.get(reminder.id)

    assert stored is not None
    assert stored.status is ReminderStatus.CANCELLED


def test_cancel_unknown_reminder_returns_false() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    cancelled = reminder_scheduler.cancel("unknown-reminder")

    assert cancelled is False

def test_reschedule_updates_time_and_replaces_schedule() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    original_trigger_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    new_trigger_at = datetime.now(timezone.utc) + timedelta(minutes=20)

    reminder = Reminder.create(
        message="Reprogramar reunión",
        trigger_at=original_trigger_at,
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.schedule(reminder)

    assert scheduler.one_shots() == [
        f"reminder:{reminder.id}",
    ]

    result = reminder_scheduler.reschedule(
        reminder.id,
        new_trigger_at,
    )

    assert result is True

    stored = reminder_scheduler.get(reminder.id)

    assert stored is not None
    assert stored.trigger_at == new_trigger_at
    assert stored.status is ReminderStatus.PENDING

    assert scheduler.one_shots() == [
        f"reminder:{reminder.id}",
    ]


def test_reschedule_removes_old_execution_before_registering_new_one() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Cambiar horario",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.schedule(reminder)

    original_schedule_count = len(scheduler.one_shots())

    reminder_scheduler.reschedule(
        reminder.id,
        datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    assert original_schedule_count == 1
    assert len(scheduler.one_shots()) == 1


def test_reschedule_cancelled_reminder_returns_false() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Reminder cancelado",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.cancel(reminder.id)

    result = reminder_scheduler.reschedule(
        reminder.id,
        datetime.now(timezone.utc) + timedelta(minutes=20),
    )

    assert result is False
    assert scheduler.one_shots() == []


def test_reschedule_unknown_reminder_returns_false() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    result = reminder_scheduler.reschedule(
        "unknown-reminder",
        datetime.now(timezone.utc) + timedelta(minutes=20),
    )

    assert result is False
    assert scheduler.one_shots() == []

def test_reconcile_schedules_pending_reminders() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder_one = Reminder.create(
        message="Reminder uno",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    reminder_two = Reminder.create(
        message="Reminder dos",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=20),
    )

    store.add(reminder_one)
    store.add(reminder_two)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    scheduled_count = reminder_scheduler.reconcile()

    assert scheduled_count == 2

    assert set(scheduler.one_shots()) == {
        f"reminder:{reminder_one.id}",
        f"reminder:{reminder_two.id}",
    }


def test_reconcile_ignores_cancelled_reminders() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Reminder cancelado",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.cancel(reminder.id)

    scheduled_count = reminder_scheduler.reconcile()

    assert scheduled_count == 0
    assert scheduler.one_shots() == []


def test_reconcile_does_not_duplicate_existing_schedule() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)
    store = ReminderStore()

    reminder = Reminder.create(
        message="Reminder existente",
        trigger_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    store.add(reminder)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=adapter,
        reminder_store=store,
    )

    reminder_scheduler.schedule(reminder)

    scheduled_count = reminder_scheduler.reconcile()

    assert scheduled_count == 0

    assert scheduler.one_shots() == [
        f"reminder:{reminder.id}",
    ]
