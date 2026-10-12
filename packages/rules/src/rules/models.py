from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RuleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    description: str | None = None
    status: RuleStatus = RuleStatus.ACTIVE
    user_id: str | None = None
    organization_id: str | None = None
    project_id: str | None = None
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        name: str,
        description: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> Rule:
        return cls(
            id=str(uuid4()),
            name=name,
            description=description,
            status=RuleStatus.ACTIVE,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )
