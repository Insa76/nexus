from datetime import datetime, timezone

import pytest

from tasks import (
    InvalidReminderSchedule,
    Reminder,
    ReminderStatus,
    reminder_to_schedule,
    transition_reminder,
)


TRIGGER_AT = datetime(
    2026,
    9,
    21,
    9,
    0,
    tzinfo=timezone.utc,
)


def test_pending_reminder_becomes_temporal_schedule() -> None:
    reminder = Reminder.create(
        message="Revisar propuesta",
        trigger_at=TRIGGER_AT,
    )

    schedule = reminder_to_schedule(reminder)

    assert schedule.execute_at == reminder.trigger_at
    assert schedule.target_id == reminder.id
    assert schedule.target_type == "reminder"


def test_reminder_message_is_preserved_as_metadata() -> None:
    reminder = Reminder.create(
        message="Llamar a Juan",
        trigger_at=TRIGGER_AT,
    )

    schedule = reminder_to_schedule(reminder)

    assert schedule.metadata["reminder_message"] == (
        "Llamar a Juan"
    )


def test_triggered_reminder_cannot_be_scheduled() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    triggered = transition_reminder(
        reminder,
        ReminderStatus.TRIGGERED,
    )

    with pytest.raises(InvalidReminderSchedule):
        reminder_to_schedule(triggered)


def test_cancelled_reminder_cannot_be_scheduled() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    cancelled = transition_reminder(
        reminder,
        ReminderStatus.CANCELLED,
    )

    with pytest.raises(InvalidReminderSchedule):
        reminder_to_schedule(cancelled)


def test_schedule_creation_does_not_mutate_reminder() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    schedule = reminder_to_schedule(reminder)

    assert reminder.status == ReminderStatus.PENDING
    assert schedule.target_id == reminder.id
