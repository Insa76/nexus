from __future__ import annotations

from context import AssistantContext

from tasks.reminders import Reminder
from tasks.reminder_store import ReminderStore


class ReminderResolver:
    """Resolves reminders relevant to an assistant context."""

    def __init__(self, store: ReminderStore) -> None:
        self._store = store

    def resolve(self, context: AssistantContext) -> list[Reminder]:
        reminders = self._store.list()

        user = context.user
        organization = context.organization
        project_ids = {project.id for project in context.projects}

        resolved: list[Reminder] = []

        for reminder in reminders:
            if user is not None and reminder.user_id == user.id:
                resolved.append(reminder)
                continue

            if (
                organization is not None
                and reminder.organization_id == organization.id
            ):
                resolved.append(reminder)
                continue

            if (
                reminder.project_id is not None
                and reminder.project_id in project_ids
            ):
                resolved.append(reminder)

        return resolved
