from __future__ import annotations

from dataclasses import dataclass

from documents.document_type import DocumentType


@dataclass(frozen=True)
class DocumentTypeDetectionEvidence:
    detected_type: DocumentType
    strategy: str

    @property
    def mime_type(self) -> str:
        return self.detected_type.mime_type
