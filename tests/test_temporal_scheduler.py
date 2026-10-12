import asyncio
from datetime import datetime, timedelta, timezone

from bootstrap.temporal_scheduler import TemporalSchedulerAdapter
from runtime.scheduler import Scheduler
from tasks import TemporalSchedule


def test_adapter_registers_temporal_schedule() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)

    schedule = TemporalSchedule.create(
        execute_at=datetime.now(timezone.utc),
        target_id="reminder-123",
        target_type="reminder",
    )

    async def callback() -> None:
        pass

    adapter.schedule(
        temporal_schedule=schedule,
        callback=callback,
    )

    assert adapter.scheduled() == [
        "reminder:reminder-123"
    ]


def test_adapter_executes_temporal_schedule() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)

    executed: list[str] = []

    schedule = TemporalSchedule.create(
        execute_at=(
            datetime.now(timezone.utc)
            - timedelta(seconds=0.01)
        ),
        target_id="reminder-123",
        target_type="reminder",
    )

    async def callback() -> None:
        executed.append(schedule.target_id)

    adapter.schedule(
        temporal_schedule=schedule,
        callback=callback,
    )

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start()
        )

        await asyncio.sleep(0.05)

        await scheduler.stop()

        await asyncio.wait_for(
            task,
            timeout=1.0,
        )

    asyncio.run(run())

    assert executed == ["reminder-123"]


def test_adapter_supports_generic_temporal_targets() -> None:
    scheduler = Scheduler()
    adapter = TemporalSchedulerAdapter(scheduler)

    schedule = TemporalSchedule.create(
        execute_at=datetime.now(timezone.utc),
        target_id="task-123",
        target_type="task",
    )

    async def callback() -> None:
        pass

    adapter.schedule(
        temporal_schedule=schedule,
        callback=callback,
    )

    assert adapter.scheduled() == [
        "task:task-123"
    ]
