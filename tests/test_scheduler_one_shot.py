
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


def test_cancel_one_shot_prevents_execution_after_scheduler_starts() -> None:
    scheduler = Scheduler()
    executions: list[str] = []

    async def callback() -> None:
        executions.append("executed")

    scheduler.register_at(
        name="cancelled-reminder",
        execute_at=(
            datetime.now(timezone.utc)
            + timedelta(seconds=0.20)
        ),
        callback=callback,
    )

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start()
        )

        # Deja que el scheduler comience a esperar la ejecución.
        await asyncio.sleep(0.03)

        assert scheduler.cancel_one_shot(
            "cancelled-reminder"
        ) is True

        # Espera más allá de la fecha programada originalmente.
        await asyncio.sleep(0.25)

        await scheduler.stop()
        await asyncio.wait_for(task, timeout=1.0)

    asyncio.run(run())

    assert executions == []


def test_stop_cancels_future_one_shot_immediately() -> None:
    scheduler = Scheduler()
    executions: list[str] = []

    async def callback() -> None:
        executions.append("executed")

    scheduler.register_at(
        name="future-reminder",
        execute_at=(
            datetime.now(timezone.utc)
            + timedelta(hours=2)
        ),
        callback=callback,
    )

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start()
        )

        await asyncio.sleep(0.02)

        await asyncio.wait_for(
            scheduler.stop(),
            timeout=1.0,
        )

        await asyncio.wait_for(
            task,
            timeout=1.0,
        )

        assert task.done()

    asyncio.run(run())

    assert executions == []


def test_register_at_from_another_thread() -> None:
    scheduler = Scheduler()
    executions: list[str] = []

    async def callback() -> None:
        executions.append("executed")

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start(keep_alive=True)
        )

        await asyncio.sleep(0.03)

        await asyncio.to_thread(
            scheduler.register_at,
            name="http-thread-reminder",
            execute_at=(
                datetime.now(timezone.utc)
                + timedelta(seconds=0.10)
            ),
            callback=callback,
        )

        await asyncio.sleep(0.20)

        await scheduler.stop()
        await asyncio.wait_for(task, timeout=1.0)

    asyncio.run(run())

    assert executions == ["executed"]


def test_cancel_one_shot_from_another_thread() -> None:
    scheduler = Scheduler()
    executions: list[str] = []

    async def callback() -> None:
        executions.append("executed")

    scheduler.register_at(
        name="http-thread-cancel",
        execute_at=(
            datetime.now(timezone.utc)
            + timedelta(seconds=0.30)
        ),
        callback=callback,
    )

    async def run() -> None:
        task = asyncio.create_task(
            scheduler.start(keep_alive=True)
        )

        await asyncio.sleep(0.03)

        cancelled = await asyncio.to_thread(
            scheduler.cancel_one_shot,
            "http-thread-cancel",
        )

        assert cancelled is True

        await asyncio.sleep(0.35)

        await scheduler.stop()
        await asyncio.wait_for(task, timeout=1.0)

    asyncio.run(run())

    assert executions == []

