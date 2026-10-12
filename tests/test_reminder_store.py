from datetime import datetime, timezone

import pytest

from tasks import Reminder, ReminderStore


TRIGGER_AT = datetime(
    2026,
    9,
    21,
    9,
    0,
    tzinfo=timezone.utc,
)


def test_store_add_and_get_reminder() -> None:
    store = ReminderStore()

    reminder = Reminder.create(
        message="Revisar propuesta",
        trigger_at=TRIGGER_AT,
    )

    store.add(reminder)

    assert store.get(reminder.id) == reminder


def test_store_list_reminders() -> None:
    store = ReminderStore()

    first = Reminder.create(
        message="Primer recordatorio",
        trigger_at=TRIGGER_AT,
    )

    second = Reminder.create(
        message="Segundo recordatorio",
        trigger_at=TRIGGER_AT,
    )

    store.add(first)
    store.add(second)

    assert store.list() == [first, second]
    assert store.count() == 2


def test_store_update_reminder() -> None:
    store = ReminderStore()

    reminder = Reminder.create(
        message="Recordatorio",
        trigger_at=TRIGGER_AT,
    )

    store.add(reminder)

    updated = Reminder(
        id=reminder.id,
        message="Recordatorio actualizado",
        trigger_at=reminder.trigger_at,
        status=reminder.status,
        task_id=reminder.task_id,
        user_id=reminder.user_id,
        organization_id=reminder.organization_id,
        project_id=reminder.project_id,
        created_at=reminder.created_at,
    )

    store.update(updated)

    assert store.get(reminder.id) == updated
    assert store.get(reminder.id).message == "Recordatorio actualizado"


def test_store_update_missing_reminder_raises() -> None:
    store = ReminderStore()

    reminder = Reminder.create(
        message="No existe",
        trigger_at=TRIGGER_AT,
    )

    with pytest.raises(KeyError):
        store.update(reminder)


def test_store_remove_reminder() -> None:
    store = ReminderStore()

    reminder = Reminder.create(
        message="Eliminar",
        trigger_at=TRIGGER_AT,
    )

    store.add(reminder)

    removed = store.remove(reminder.id)

    assert removed == reminder
    assert store.get(reminder.id) is None
    assert store.count() == 0


def test_store_remove_missing_reminder_is_safe() -> None:
    store = ReminderStore()

    assert store.remove("missing-reminder") is None


def test_store_clear() -> None:
    store = ReminderStore()

    store.add(
        Reminder.create(
            message="Primero",
            trigger_at=TRIGGER_AT,
        )
    )

    store.add(
        Reminder.create(
            message="Segundo",
            trigger_at=TRIGGER_AT,
        )
    )

    store.clear()

    assert store.list() == []
    assert store.count() == 0
