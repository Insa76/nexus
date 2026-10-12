from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    priority: str = "normal"
    user_id: str | None = None
    organization_id: str | None = None
    project_id: str | None = None
    due_at: datetime | None = None
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        title: str,
        description: str | None = None,
        priority: str = "normal",
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
        due_at: datetime | None = None,
    ) -> Task:
        return cls(
            id=str(uuid4()),
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
            due_at=due_at,
        )
