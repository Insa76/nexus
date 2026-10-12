from datetime import datetime, timezone

import pytest

from tasks import (
    InvalidReminderTransition,
    Reminder,
    ReminderStatus,
    ReminderTriggerHandler,
)


TRIGGER_AT = datetime(
    2026,
    9,
    21,
    9,
    0,
    tzinfo=timezone.utc,
)


def test_handler_triggers_pending_reminder() -> None:
    reminder = Reminder.create(
        message="Revisar propuesta",
        trigger_at=TRIGGER_AT,
    )

    handler = ReminderTriggerHandler()

    result = handler.handle(reminder)

    assert result.reminder_id == reminder.id
    assert result.message == reminder.message
    assert result.reminder.status == ReminderStatus.TRIGGERED
    assert result.triggered_at.tzinfo == timezone.utc


def test_handler_does_not_mutate_original_reminder() -> None:
    reminder = Reminder.create(
        message="Llamar a Juan",
        trigger_at=TRIGGER_AT,
    )

    handler = ReminderTriggerHandler()

    result = handler.handle(reminder)

    assert reminder.status == ReminderStatus.PENDING
    assert result.reminder.status == ReminderStatus.TRIGGERED


def test_handler_preserves_reminder_identity() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
        task_id="task-123",
        user_id="user-123",
        organization_id="org-123",
        project_id="project-123",
    )

    handler = ReminderTriggerHandler()

    result = handler.handle(reminder)

    triggered = result.reminder

    assert triggered.id == reminder.id
    assert triggered.task_id == reminder.task_id
    assert triggered.user_id == reminder.user_id
    assert triggered.organization_id == reminder.organization_id
    assert triggered.project_id == reminder.project_id
    assert triggered.trigger_at == reminder.trigger_at


def test_handler_cannot_trigger_triggered_reminder() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    handler = ReminderTriggerHandler()

    first = handler.handle(reminder)

    with pytest.raises(InvalidReminderTransition):
        handler.handle(first.reminder)


def test_handler_cannot_trigger_cancelled_reminder() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    from tasks import transition_reminder

    cancelled = transition_reminder(
        reminder,
        ReminderStatus.CANCELLED,
    )

    handler = ReminderTriggerHandler()

    with pytest.raises(InvalidReminderTransition):
        handler.handle(cancelled)
