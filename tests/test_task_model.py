from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tasks import Task, TaskStatus


def test_task_creation() -> None:
    task = Task.create(
        title="Preparar reunión",
        description="Preparar agenda",
        priority="high",
    )

    assert task.id
    assert task.title == "Preparar reunión"
    assert task.description == "Preparar agenda"
    assert task.priority == "high"
    assert task.status == TaskStatus.PENDING


def test_task_with_due_date() -> None:
    due_at = datetime(2026, 10, 1, 15, 0, tzinfo=timezone.utc)

    task = Task.create(
        title="Entregar informe",
        due_at=due_at,
    )

    assert task.due_at == due_at


def test_task_ids_are_unique() -> None:
    first = Task.create(title="Primera")
    second = Task.create(title="Segunda")

    assert first.id != second.id


def test_task_is_immutable() -> None:
    task = Task.create(title="Inmutable")

    with pytest.raises(FrozenInstanceError):
        task.title = "Modificada"  # type: ignore[misc]
