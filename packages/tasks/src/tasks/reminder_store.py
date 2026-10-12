from __future__ import annotations

from tasks.reminders import Reminder


class ReminderStore:
    """In-memory store for assistant reminders."""

    def __init__(self) -> None:
        self._reminders: dict[str, Reminder] = {}

    def add(self, reminder: Reminder) -> Reminder:
        self._reminders[reminder.id] = reminder
        return reminder

    def get(self, reminder_id: str) -> Reminder | None:
        return self._reminders.get(reminder_id)

    def list(self) -> list[Reminder]:
        return list(self._reminders.values())

    def update(self, reminder: Reminder) -> Reminder:
        if reminder.id not in self._reminders:
            raise KeyError(f"Reminder not found: {reminder.id}")

        self._reminders[reminder.id] = reminder
        return reminder

    def remove(self, reminder_id: str) -> Reminder | None:
        return self._reminders.pop(reminder_id, None)

    def clear(self) -> None:
        self._reminders.clear()

    def count(self) -> int:
        return len(self._reminders)
