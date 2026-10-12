from bootstrap.assistant_services import AssistantServices
from bootstrap.assistant_services_lifecycle import (
    AssistantServicesLifecycle,
)
from bootstrap.bootstrap import build_assistant_runtime
from engine.engine import Engine
from tasks import Reminder, ReminderStatus


def test_build_assistant_runtime() -> None:
    engine, services, lifecycle = build_assistant_runtime()

    assert isinstance(engine, Engine)
    assert isinstance(services, AssistantServices)
    assert isinstance(
        lifecycle,
        AssistantServicesLifecycle,
    )


def test_build_assistant_runtime_keeps_engine_and_services_separate() -> None:
    engine, services, lifecycle = build_assistant_runtime()

    assert engine is not services
    assert engine is not lifecycle
    assert services is not lifecycle

    assert services.reminder_scheduler is not None
    assert services.scheduler is not None


def test_lifecycle_controls_assistant_services() -> None:
    engine, services, lifecycle = build_assistant_runtime()

    assert lifecycle.services is services
    assert lifecycle.running is False

import asyncio
from datetime import datetime, timedelta, timezone

from tasks import ReminderStatus


def test_assistant_runtime_executes_reminder_end_to_end() -> None:
    engine, services, lifecycle = build_assistant_runtime()

    reminder = services.reminder_store.add(
        Reminder.create(
            message="Reminder end-to-end",
            trigger_at=datetime.now(timezone.utc) + timedelta(
                seconds=0.05
            ),
        )
    )

    services.reminder_scheduler.schedule(reminder)

    async def run() -> None:
        await lifecycle.start()

        await asyncio.sleep(0.15)

        await lifecycle.stop()

    asyncio.run(run())

    stored = services.reminder_store.get(reminder.id)

    assert stored is not None
    assert stored.status is ReminderStatus.TRIGGERED
    assert lifecycle.running is False
