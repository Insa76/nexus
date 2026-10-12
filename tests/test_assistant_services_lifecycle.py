from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from bootstrap.assistant_services import (
    AssistantServices,
    build_assistant_services,
)
from bootstrap.assistant_services_lifecycle import (
    AssistantServicesLifecycle,
)
from tasks import Reminder


def test_start_runs_scheduler_in_background() -> None:
    services = build_assistant_services()
    lifecycle = AssistantServicesLifecycle(services)

    async def run() -> None:
        await lifecycle.start()

        assert lifecycle.running is True
        assert lifecycle._scheduler_task is not None
        assert not lifecycle._scheduler_task.done()

        await lifecycle.stop()

    asyncio.run(run())


def test_stop_stops_background_scheduler() -> None:
    services = build_assistant_services()
    lifecycle = AssistantServicesLifecycle(services)

    async def run() -> None:
        await lifecycle.start()
        await lifecycle.stop()

        assert lifecycle.running is False
        assert lifecycle._scheduler_task is None

    asyncio.run(run())


def test_scheduler_executes_pending_reminder_in_background() -> None:
    services = build_assistant_services()

    reminder = Reminder.create(
        message="Reminder de prueba",
        trigger_at=datetime.now(timezone.utc) + timedelta(
            seconds=0.05
        ),
    )

    services.reminder_store.add(reminder)
    services.reminder_scheduler.schedule(reminder)

    lifecycle = AssistantServicesLifecycle(services)

    async def run() -> None:
        await lifecycle.start()

        await asyncio.sleep(0.15)

        await lifecycle.stop()

    asyncio.run(run())

    triggered = services.reminder_store.get(reminder.id)

    assert triggered is not None
    assert triggered.status.value == "triggered"


def test_start_is_idempotent() -> None:
    services = build_assistant_services()
    lifecycle = AssistantServicesLifecycle(services)

    async def run() -> None:
        await lifecycle.start()

        first_task = lifecycle._scheduler_task

        await lifecycle.start()

        assert lifecycle._scheduler_task is first_task

        await lifecycle.stop()

    asyncio.run(run())
