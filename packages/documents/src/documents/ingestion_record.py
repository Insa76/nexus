from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4

from documents.document_type import DocumentType


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class DocumentIngestionRecord:
    """
    Immutable record of a document ingestion attempt that produced content.

    The record represents historical ingestion state. It does not replace
    the current ingestion_evidence stored on Document.
    """

    id: str
    document_id: str
    artifact_id: str
    content_id: str

    declared_type: DocumentType
    detected_type: DocumentType | None = None
    detection_strategy: str | None = None
    type_matches: bool | None = None

    created_at: datetime = field(default_factory=_utc_now)

    @classmethod
    def create(
        cls,
        *,
        document_id: str,
        artifact_id: str,
        content_id: str,
        declared_type: str | DocumentType,
        detected_type: str | DocumentType | None = None,
        detection_strategy: str | None = None,
        type_matches: bool | None = None,
    ) -> DocumentIngestionRecord:
        resolved_declared_type = (
            declared_type
            if isinstance(declared_type, DocumentType)
            else DocumentType.from_mime_type(declared_type)
        )

        resolved_detected_type = None

        if detected_type is not None:
            resolved_detected_type = (
                detected_type
                if isinstance(detected_type, DocumentType)
                else DocumentType.from_mime_type(detected_type)
            )

        resolved_type_matches = type_matches

        if (
            resolved_type_matches is None
            and resolved_detected_type is not None
        ):
            resolved_type_matches = (
                resolved_declared_type.mime_type
                == resolved_detected_type.mime_type
            )

        return cls(
            id=str(uuid4()),
            document_id=document_id,
            artifact_id=artifact_id,
            content_id=content_id,
            declared_type=resolved_declared_type,
            detected_type=resolved_detected_type,
            detection_strategy=detection_strategy,
            type_matches=resolved_type_matches,
            created_at=_utc_now(),
        )

    @property
    def type_mismatch(self) -> bool | None:
        if self.type_matches is None:
            return None

        return not self.type_matches
