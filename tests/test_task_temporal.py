from datetime import datetime, timedelta, timezone

from tasks import (
    Task,
    TaskStatus,
    due_tasks,
    overdue_tasks,
    transition_task,
    upcoming_tasks,
)


def test_overdue_tasks_returns_past_pending_tasks() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Tarea vencida",
        due_at=now - timedelta(hours=1),
    )

    assert overdue_tasks([task], now) == [task]


def test_overdue_tasks_excludes_future_tasks() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Tarea futura",
        due_at=now + timedelta(hours=1),
    )

    assert overdue_tasks([task], now) == []


def test_due_tasks_includes_task_at_current_time() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Tarea ahora",
        due_at=now,
    )

    assert due_tasks([task], now) == [task]


def test_due_tasks_includes_overdue_tasks() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Tarea vencida",
        due_at=now - timedelta(minutes=30),
    )

    assert due_tasks([task], now) == [task]


def test_upcoming_tasks_returns_future_tasks() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Tarea próxima",
        due_at=now + timedelta(hours=2),
    )

    assert upcoming_tasks([task], now) == [task]


def test_tasks_without_due_date_are_excluded() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(title="Sin fecha")

    assert overdue_tasks([task], now) == []
    assert due_tasks([task], now) == []
    assert upcoming_tasks([task], now) == []


def test_completed_tasks_are_excluded() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Completada",
        due_at=now - timedelta(hours=1),
    )

    completed = transition_task(task, TaskStatus.IN_PROGRESS)
    completed = transition_task(completed, TaskStatus.COMPLETED)

    assert overdue_tasks([completed], now) == []
    assert due_tasks([completed], now) == []


def test_cancelled_tasks_are_excluded() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Cancelada",
        due_at=now - timedelta(hours=1),
    )

    cancelled = transition_task(task, TaskStatus.CANCELLED)

    assert overdue_tasks([cancelled], now) == []
    assert due_tasks([cancelled], now) == []


def test_temporal_queries_preserve_task_order() -> None:
    now = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)

    first = Task.create(
        title="Primera",
        due_at=now + timedelta(hours=1),
    )

    second = Task.create(
        title="Segunda",
        due_at=now + timedelta(hours=2),
    )

    third = Task.create(
        title="Tercera",
        due_at=now + timedelta(hours=3),
    )

    tasks = [first, second, third]

    assert upcoming_tasks(tasks, now) == tasks
