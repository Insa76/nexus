import asyncio
from datetime import datetime, timedelta, timezone

from runtime.scheduler import Scheduler


def test_register_at_registers_one_shot() -> None:
    scheduler = Scheduler()

    async def callback() -> None:
        pass

    execute_at = datetime.now(timezone.utc)

    scheduler.register_at(
        name="test-reminder",
        execute_at=execute_at,
        callback=callback,
    )

    assert scheduler.one_shots() == ["test-reminder"]


def test_one_shot_executes_once() -> None:
    scheduler = Scheduler()
    executions: list[str] = []

    async def callback() -> None:
        executions.append("executed")

    execute_at = (
        datetime.now(timezone.utc)
        - timedelta(seconds=0.01)
    )

    scheduler.register_at(
        name="test-reminder",
        execute_at=execute_at,
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

    assert executions == ["executed"]


def test_one_shot_waits_until_execute_at() -> None:
    scheduler = Scheduler()
    executions: list[float] = []

    start = datetime.now(timezone.utc)

    async def callback() -> None:
        elapsed = (
            datetime.now(timezone.utc) - start
        ).total_seconds()

        executions.append(elapsed)

    execute_at = (
        start + timedelta(seconds=0.08)
    )

    scheduler.register_at(
        name="delayed-reminder",
        execute_at=execute_at,
        callback=callback,
    )

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start()
        )

        await asyncio.sleep(0.03)

        assert executions == []

        await asyncio.sleep(0.10)

        await scheduler.stop()

        await asyncio.wait_for(
            task,
            timeout=1.0,
        )

    asyncio.run(run())

    assert len(executions) == 1
    assert executions[0] >= 0.07


def test_stop_prevents_future_one_shot_execution() -> None:
    scheduler = Scheduler()
    executions: list[str] = []

    async def callback() -> None:
        executions.append("executed")

    execute_at = (
        datetime.now(timezone.utc)
        + timedelta(seconds=0.15)
    )

    scheduler.register_at(
        name="future-reminder",
        execute_at=execute_at,
        callback=callback,
    )

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start()
        )

        await asyncio.sleep(0.02)

        await scheduler.stop()

        await asyncio.wait_for(
            task,
            timeout=1.0,
        )

        await asyncio.sleep(0.18)

    asyncio.run(run())

    assert executions == []


def test_clear_removes_periodic_and_one_shot_tasks() -> None:
    scheduler = Scheduler()

    async def callback() -> None:
        pass

    scheduler.register(
        name="periodic",
        interval=60,
        callback=callback,
    )

    scheduler.register_at(
        name="one-shot",
        execute_at=datetime.now(timezone.utc),
        callback=callback,
    )

    scheduler.clear()

    assert scheduler.tasks() == []
    assert scheduler.one_shots() == []
