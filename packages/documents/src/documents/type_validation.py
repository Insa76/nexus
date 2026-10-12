from __future__ import annotations

from dataclasses import dataclass

from documents.document_type import DocumentType


@dataclass(frozen=True)
class DocumentTypeValidation:
    declared_type: DocumentType
    detected_type: DocumentType

    @property
    def matches(self) -> bool:
        return (
            self.declared_type.mime_type
            == self.detected_type.mime_type
        )

    @property
    def mismatch(self) -> bool:
        return not self.matches
