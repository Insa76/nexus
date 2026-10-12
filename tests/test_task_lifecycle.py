import pytest

from tasks import (
    InvalidTaskTransition,
    Task,
    TaskStatus,
    can_transition,
    transition_task,
)


def test_pending_can_start() -> None:
    assert can_transition(
        TaskStatus.PENDING,
        TaskStatus.IN_PROGRESS,
    )


def test_pending_can_be_cancelled() -> None:
    assert can_transition(
        TaskStatus.PENDING,
        TaskStatus.CANCELLED,
    )


def test_in_progress_can_complete() -> None:
    assert can_transition(
        TaskStatus.IN_PROGRESS,
        TaskStatus.COMPLETED,
    )


def test_in_progress_can_be_cancelled() -> None:
    assert can_transition(
        TaskStatus.IN_PROGRESS,
        TaskStatus.CANCELLED,
    )


def test_completed_has_no_outgoing_transitions() -> None:
    assert not can_transition(
        TaskStatus.COMPLETED,
        TaskStatus.IN_PROGRESS,
    )

    assert not can_transition(
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    )


def test_cancelled_has_no_outgoing_transitions() -> None:
    assert not can_transition(
        TaskStatus.CANCELLED,
        TaskStatus.PENDING,
    )

    assert not can_transition(
        TaskStatus.CANCELLED,
        TaskStatus.IN_PROGRESS,
    )


def test_transition_task_returns_new_task() -> None:
    task = Task.create(title="Preparar reunión")

    started = transition_task(
        task,
        TaskStatus.IN_PROGRESS,
    )

    assert started.id == task.id
    assert started.title == task.title
    assert started.status == TaskStatus.IN_PROGRESS
    assert task.status == TaskStatus.PENDING


def test_transition_task_can_complete() -> None:
    task = Task.create(title="Preparar reunión")

    started = transition_task(
        task,
        TaskStatus.IN_PROGRESS,
    )

    completed = transition_task(
        started,
        TaskStatus.COMPLETED,
    )

    assert completed.status == TaskStatus.COMPLETED


def test_invalid_transition_raises() -> None:
    task = Task.create(title="Tarea")

    with pytest.raises(InvalidTaskTransition):
        transition_task(
            task,
            TaskStatus.COMPLETED,
        )


def test_completed_task_cannot_be_reopened() -> None:
    task = Task.create(title="Tarea")

    started = transition_task(
        task,
        TaskStatus.IN_PROGRESS,
    )

    completed = transition_task(
        started,
        TaskStatus.COMPLETED,
    )

    with pytest.raises(InvalidTaskTransition):
        transition_task(
            completed,
            TaskStatus.IN_PROGRESS,
        )
