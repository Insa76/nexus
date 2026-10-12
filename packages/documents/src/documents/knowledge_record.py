from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from documents.knowledge import DocumentKnowledge


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentKnowledgeRecord:
    id: str
    document_id: str
    content_version_id: str
    knowledge: DocumentKnowledge
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        document_id: str,
        content_version_id: str,
        knowledge: DocumentKnowledge,
    ) -> DocumentKnowledgeRecord:
        return cls(
            id=str(uuid4()),
            document_id=document_id,
            content_version_id=content_version_id,
            knowledge=knowledge,
            created_at=_utc_now(),
        )
