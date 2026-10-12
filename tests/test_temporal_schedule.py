from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from tasks import TemporalSchedule


EXECUTE_AT = datetime(
    2026,
    9,
    21,
    9,
    0,
    tzinfo=timezone.utc,
)


def test_temporal_schedule_creation() -> None:
    schedule = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="reminder-123",
        target_type="reminder",
    )

    assert schedule.id
    assert schedule.execute_at == EXECUTE_AT
    assert schedule.target_id == "reminder-123"
    assert schedule.target_type == "reminder"


def test_temporal_schedule_can_have_metadata() -> None:
    schedule = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="reminder-123",
        target_type="reminder",
        metadata={
            "source": "assistant",
            "priority": "normal",
        },
    )

    assert schedule.metadata == {
        "source": "assistant",
        "priority": "normal",
    }


def test_temporal_schedule_ids_are_unique() -> None:
    first = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="reminder-1",
        target_type="reminder",
    )

    second = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="reminder-2",
        target_type="reminder",
    )

    assert first.id != second.id


def test_temporal_schedule_is_immutable() -> None:
    schedule = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="reminder-123",
        target_type="reminder",
    )

    with pytest.raises(FrozenInstanceError):
        schedule.target_id = "other-target"  # type: ignore[misc]


def test_temporal_schedule_copies_metadata() -> None:
    metadata = {
        "source": "assistant",
    }

    schedule = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="reminder-123",
        target_type="reminder",
        metadata=metadata,
    )

    metadata["source"] = "modified"

    assert schedule.metadata["source"] == "assistant"


def test_temporal_schedule_can_target_other_domains() -> None:
    schedule = TemporalSchedule.create(
        execute_at=EXECUTE_AT,
        target_id="task-123",
        target_type="task",
    )

    assert schedule.target_id == "task-123"
    assert schedule.target_type == "task"
