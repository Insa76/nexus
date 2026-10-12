from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tasks import Reminder, ReminderStatus


def test_reminder_creation() -> None:
    trigger_at = datetime(
        2026,
        9,
        21,
        9,
        0,
        tzinfo=timezone.utc,
    )

    reminder = Reminder.create(
        message="Revisar la propuesta",
        trigger_at=trigger_at,
    )

    assert reminder.id
    assert reminder.message == "Revisar la propuesta"
    assert reminder.trigger_at == trigger_at
    assert reminder.status == ReminderStatus.PENDING
    assert reminder.task_id is None


def test_reminder_can_reference_task() -> None:
    trigger_at = datetime(
        2026,
        9,
        21,
        9,
        0,
        tzinfo=timezone.utc,
    )

    reminder = Reminder.create(
        message="Revisar la propuesta",
        trigger_at=trigger_at,
        task_id="task-123",
    )

    assert reminder.task_id == "task-123"


def test_reminder_can_have_context_references() -> None:
    trigger_at = datetime(
        2026,
        9,
        21,
        9,
        0,
        tzinfo=timezone.utc,
    )

    reminder = Reminder.create(
        message="Reunión de equipo",
        trigger_at=trigger_at,
        user_id="user-123",
        organization_id="org-123",
        project_id="project-123",
    )

    assert reminder.user_id == "user-123"
    assert reminder.organization_id == "org-123"
    assert reminder.project_id == "project-123"


def test_reminder_ids_are_unique() -> None:
    trigger_at = datetime(
        2026,
        9,
        21,
        9,
        0,
        tzinfo=timezone.utc,
    )

    first = Reminder.create(
        message="Primer recordatorio",
        trigger_at=trigger_at,
    )

    second = Reminder.create(
        message="Segundo recordatorio",
        trigger_at=trigger_at,
    )

    assert first.id != second.id


def test_reminder_is_immutable() -> None:
    trigger_at = datetime(
        2026,
        9,
        21,
        9,
        0,
        tzinfo=timezone.utc,
    )

    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=trigger_at,
    )

    with pytest.raises(FrozenInstanceError):
        reminder.message = "Modificado"  # type: ignore[misc]


def test_reminder_default_status_is_pending() -> None:
    trigger_at = datetime(
        2026,
        9,
        21,
        9,
        0,
        tzinfo=timezone.utc,
    )

    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=trigger_at,
    )

    assert reminder.status == ReminderStatus.PENDING
