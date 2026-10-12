from datetime import datetime, timezone

import pytest

from tasks import (
    InvalidReminderTransition,
    Reminder,
    ReminderStatus,
    can_reminder_transition,
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


def test_pending_can_be_triggered() -> None:
    assert can_reminder_transition(
        ReminderStatus.PENDING,
        ReminderStatus.TRIGGERED,
    )


def test_pending_can_be_cancelled() -> None:
    assert can_reminder_transition(
        ReminderStatus.PENDING,
        ReminderStatus.CANCELLED,
    )


def test_triggered_has_no_outgoing_transitions() -> None:
    assert not can_reminder_transition(
        ReminderStatus.TRIGGERED,
        ReminderStatus.PENDING,
    )

    assert not can_reminder_transition(
        ReminderStatus.TRIGGERED,
        ReminderStatus.CANCELLED,
    )


def test_cancelled_has_no_outgoing_transitions() -> None:
    assert not can_reminder_transition(
        ReminderStatus.CANCELLED,
        ReminderStatus.PENDING,
    )

    assert not can_reminder_transition(
        ReminderStatus.CANCELLED,
        ReminderStatus.TRIGGERED,
    )


def test_transition_to_triggered_returns_new_reminder() -> None:
    reminder = Reminder.create(
        message="Revisar propuesta",
        trigger_at=TRIGGER_AT,
    )

    triggered = transition_reminder(
        reminder,
        ReminderStatus.TRIGGERED,
    )

    assert triggered.id == reminder.id
    assert triggered.message == reminder.message
    assert triggered.trigger_at == reminder.trigger_at
    assert triggered.status == ReminderStatus.TRIGGERED
    assert reminder.status == ReminderStatus.PENDING


def test_transition_to_cancelled_returns_new_reminder() -> None:
    reminder = Reminder.create(
        message="Cancelar reunión",
        trigger_at=TRIGGER_AT,
    )

    cancelled = transition_reminder(
        reminder,
        ReminderStatus.CANCELLED,
    )

    assert cancelled.id == reminder.id
    assert cancelled.status == ReminderStatus.CANCELLED
    assert reminder.status == ReminderStatus.PENDING


def test_triggered_reminder_cannot_be_reopened() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    triggered = transition_reminder(
        reminder,
        ReminderStatus.TRIGGERED,
    )

    with pytest.raises(InvalidReminderTransition):
        transition_reminder(
            triggered,
            ReminderStatus.PENDING,
        )


def test_triggered_reminder_cannot_be_cancelled() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    triggered = transition_reminder(
        reminder,
        ReminderStatus.TRIGGERED,
    )

    with pytest.raises(InvalidReminderTransition):
        transition_reminder(
            triggered,
            ReminderStatus.CANCELLED,
        )


def test_cancelled_reminder_cannot_be_reopened() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    cancelled = transition_reminder(
        reminder,
        ReminderStatus.CANCELLED,
    )

    with pytest.raises(InvalidReminderTransition):
        transition_reminder(
            cancelled,
            ReminderStatus.PENDING,
        )


def test_invalid_pending_to_pending_transition() -> None:
    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    with pytest.raises(InvalidReminderTransition):
        transition_reminder(
            reminder,
            ReminderStatus.PENDING,
        )
