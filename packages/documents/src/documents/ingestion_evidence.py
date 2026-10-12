from __future__ import annotations

from dataclasses import dataclass

from documents.document_type import DocumentType


@dataclass(frozen=True)
class DocumentIngestionEvidence:
    declared_type: DocumentType
    detected_type: DocumentType
    detection_strategy: str

    @property
    def matches(self) -> bool:
        return (
            self.declared_type.mime_type
            == self.detected_type.mime_type
        )

    @property
    def mismatch(self) -> bool:
        return not self.matches
