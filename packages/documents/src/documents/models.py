from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from documents.ingestion_evidence import DocumentIngestionEvidence


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Document:
    id: str
    name: str
    mime_type: str
    source: str
    description: str | None = None
    user_id: str | None = None
    organization_id: str | None = None
    project_id: str | None = None
    artifact_id: str | None = None
    content_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)
    ingestion_evidence: DocumentIngestionEvidence | None = None

    @classmethod
    def create(
        cls,
        name: str,
        mime_type: str,
        source: str,
        description: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
        artifact_id: str | None = None,
        content_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> Document:
        now = _utc_now()

        normalized_metadata = {
            str(key): str(value)
            for key, value in (metadata or {}).items()
        }

        return cls(
            id=str(uuid4()),
            name=name,
            mime_type=mime_type,
            source=source,
            description=description,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
            artifact_id=artifact_id,
            content_id=content_id,
            metadata=normalized_metadata,
            created_at=now,
            updated_at=now,
        )
