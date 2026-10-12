from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from documents.document_type import DocumentType


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentContentVersion:
    """
    Immutable historical version of a document's content.

    A version identifies the content produced at a particular point in
    the document lifecycle. It does not replace DocumentContent.
    """

    id: str
    document_id: str
    content_id: str
    version: int

    content_type: DocumentType

    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        *,
        document_id: str,
        content_id: str,
        version: int,
        content_type: str | DocumentType,
    ) -> DocumentContentVersion:
        if version < 1:
            raise ValueError(
                "Document content version must be greater than zero"
            )

        resolved_content_type = (
            content_type
            if isinstance(content_type, DocumentType)
            else DocumentType.from_mime_type(content_type)
        )

        return cls(
            id=str(uuid4()),
            document_id=document_id,
            content_id=content_id,
            version=version,
            content_type=resolved_content_type,
            created_at=_utc_now(),
        )
