from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentArtifact:
    """
    Representa el artefacto físico o digital asociado a un documento.

    El modelo describe el artefacto, pero no realiza operaciones
    de almacenamiento, lectura o hashing.
    """

    id: str
    location: str
    size: int | None = None
    checksum: str | None = None
    checksum_algorithm: str | None = None
    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        location: str,
        size: int | None = None,
        checksum: str | None = None,
        checksum_algorithm: str | None = None,
    ) -> DocumentArtifact:
        return cls(
            id=str(uuid4()),
            location=location,
            size=size,
            checksum=checksum,
            checksum_algorithm=checksum_algorithm,
            created_at=_utc_now(),
        )
