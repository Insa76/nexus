
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bootstrap.assistant_services import build_assistant_services
from bootstrap.assistant_services_lifecycle import AssistantServicesLifecycle
from tasks import Reminder, ReminderStatus, ReminderStore


def test_reminders_persist_after_reopening_database(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "reminders.db"
    trigger_at = datetime(2026, 12, 1, 15, 30, tzinfo=timezone.utc)

    first = ReminderStore(db_path)
    reminder = Reminder.create(
        message="Revisar propuesta",
        trigger_at=trigger_at,
        task_id="task-1",
        user_id="user-1",
        organization_id="org-1",
        project_id="project-1",
    )
    first.add(reminder)
    first.close()

    second = ReminderStore(db_path)
    restored = second.get(reminder.id)

    assert restored == reminder
    assert restored is not None
    assert restored.status is ReminderStatus.PENDING
    assert restored.task_id == "task-1"
    assert restored.user_id == "user-1"
    assert restored.organization_id == "org-1"
    assert restored.project_id == "project-1"

    second.close()


def test_reminder_updates_and_removal_persist(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "reminders.db"
    store = ReminderStore(db_path)

    reminder = Reminder.create(
        message="Recordatorio original",
        trigger_at=datetime(2026, 12, 1, tzinfo=timezone.utc),
    )
    store.add(reminder)

    updated = Reminder(
        id=reminder.id,
        message="Recordatorio actualizado",
        trigger_at=reminder.trigger_at,
        status=ReminderStatus.CANCELLED,
        task_id=reminder.task_id,
        user_id=reminder.user_id,
        organization_id=reminder.organization_id,
        project_id=reminder.project_id,
        created_at=reminder.created_at,
    )
    store.update(updated)
    store.close()

    reopened = ReminderStore(db_path)
    assert reopened.get(reminder.id) == updated
    assert reopened.remove(reminder.id) == updated
    assert reopened.get(reminder.id) is None
    reopened.close()

    final_store = ReminderStore(db_path)
    assert final_store.count() == 0
    final_store.close()


def test_lifecycle_restores_pending_reminder_after_restart(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "reminders.db"

    first_services = build_assistant_services(db_path)
    reminder = Reminder.create(
        message="Recordatorio recuperado",
        trigger_at=datetime.now(timezone.utc) + timedelta(seconds=0.2),
    )
    first_services.reminder_store.add(reminder)

    # Simula el cierre del proceso: los datos permanecen en SQLite.
    first_services.reminder_store.close()

    second_services = build_assistant_services(db_path)
    lifecycle = AssistantServicesLifecycle(second_services)

    async def run() -> None:
        await lifecycle.start()
        await asyncio.sleep(0.5)
        await lifecycle.stop()

    asyncio.run(run())

    restored = second_services.reminder_store.get(reminder.id)
    assert restored is not None
    assert restored.status is ReminderStatus.TRIGGERED

    second_services.reminder_store.close()
