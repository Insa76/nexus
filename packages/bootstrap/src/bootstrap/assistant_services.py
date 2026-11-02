
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from runtime.scheduler import Scheduler
from tasks import ReminderStore

from bootstrap.reminder_scheduler import ReminderScheduler
from bootstrap.temporal_scheduler import TemporalSchedulerAdapter


@dataclass(slots=True)
class AssistantServices:
    scheduler: Scheduler
    reminder_store: ReminderStore
    temporal_scheduler: TemporalSchedulerAdapter
    reminder_scheduler: ReminderScheduler


def build_assistant_services(
    reminder_db_path: str | Path | None = None,
) -> AssistantServices:
    scheduler = Scheduler()

    if reminder_db_path is None:
        reminder_db_path = os.environ.get(
            "NEXUS_REMINDERS_DB_PATH",
            str(Path.home() / ".nexus" / "reminders.db"),
        )

    reminder_store = ReminderStore(db_path=reminder_db_path)
    temporal_scheduler = TemporalSchedulerAdapter(scheduler)

    reminder_scheduler = ReminderScheduler(
        scheduler_adapter=temporal_scheduler,
        reminder_store=reminder_store,
    )

    return AssistantServices(
        scheduler=scheduler,
        reminder_store=reminder_store,
        temporal_scheduler=temporal_scheduler,
        reminder_scheduler=reminder_scheduler,
    )
