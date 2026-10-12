from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class TemporalSchedule:
    """
    Representa una solicitud de ejecución temporal de una sola vez.

    Es una frontera entre el dominio que necesita una ejecución temporal
    y la infraestructura que finalmente decidirá cómo ejecutarla.
    """

    id: str
    execute_at: datetime
    target_id: str
    target_type: str
    created_at: datetime = field(default_factory=_utc_now)
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        execute_at: datetime,
        target_id: str,
        target_type: str,
        metadata: dict[str, str] | None = None,
    ) -> TemporalSchedule:
        return cls(
            id=str(uuid4()),
            execute_at=execute_at,
            target_id=target_id,
            target_type=target_type,
            metadata=dict(metadata or {}),
        )
