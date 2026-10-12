from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReminderStatus(str, Enum):
    PENDING = "pending"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Reminder:
    id: str
    message: str
    trigger_at: datetime
    status: ReminderStatus = ReminderStatus.PENDING
    task_id: str | None = None
    user_id: str | None = None
    organization_id: str | None = None
    project_id: str | None = None
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        message: str,
        trigger_at: datetime,
        task_id: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> Reminder:
        return cls(
            id=str(uuid4()),
            message=message,
            trigger_at=trigger_at,
            status=ReminderStatus.PENDING,
            task_id=task_id,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )
