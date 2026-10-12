from __future__ import annotations

from tasks.reminders import Reminder, ReminderStatus
from tasks.temporal_schedule import TemporalSchedule


class InvalidReminderSchedule(ValueError):
    """Raised when a reminder cannot be scheduled."""


def reminder_to_schedule(
    reminder: Reminder,
) -> TemporalSchedule:
    if reminder.status != ReminderStatus.PENDING:
        raise InvalidReminderSchedule(
            "Only pending reminders can be scheduled."
        )

    return TemporalSchedule.create(
        execute_at=reminder.trigger_at,
        target_id=reminder.id,
        target_type="reminder",
        metadata={
            "reminder_message": reminder.message,
        },
    )
