from __future__ import annotations

from tasks.reminders import Reminder, ReminderStatus


_ALLOWED_TRANSITIONS: dict[
    ReminderStatus,
    set[ReminderStatus],
] = {
    ReminderStatus.PENDING: {
        ReminderStatus.TRIGGERED,
        ReminderStatus.CANCELLED,
    },
    ReminderStatus.TRIGGERED: set(),
    ReminderStatus.CANCELLED: set(),
}


class InvalidReminderTransition(ValueError):
    """Raised when a reminder lifecycle transition is not allowed."""


def can_transition(
    current: ReminderStatus,
    target: ReminderStatus,
) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def transition_reminder(
    reminder: Reminder,
    target: ReminderStatus,
) -> Reminder:
    if not can_transition(reminder.status, target):
        raise InvalidReminderTransition(
            f"Invalid reminder transition: "
            f"{reminder.status.value} -> {target.value}"
        )

    return Reminder(
        id=reminder.id,
        message=reminder.message,
        trigger_at=reminder.trigger_at,
        status=target,
        task_id=reminder.task_id,
        user_id=reminder.user_id,
        organization_id=reminder.organization_id,
        project_id=reminder.project_id,
        created_at=reminder.created_at,
    )
