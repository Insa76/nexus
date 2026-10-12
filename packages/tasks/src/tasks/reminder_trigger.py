from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from tasks.reminder_lifecycle import (
    InvalidReminderTransition,
    transition_reminder,
)
from tasks.reminders import Reminder, ReminderStatus


@dataclass(frozen=True)
class ReminderTriggerResult:
    reminder_id: str
    message: str
    triggered_at: datetime
    reminder: Reminder


class ReminderTriggerHandler:
    """Handles the domain transition produced by a reminder trigger."""

    def handle(
        self,
        reminder: Reminder,
    ) -> ReminderTriggerResult:
        triggered_at = datetime.now(timezone.utc)

        triggered = transition_reminder(
            reminder,
            ReminderStatus.TRIGGERED,
        )

        return ReminderTriggerResult(
            reminder_id=triggered.id,
            message=triggered.message,
            triggered_at=triggered_at,
            reminder=triggered,
        )
