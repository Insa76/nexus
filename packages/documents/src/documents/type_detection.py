from __future__ import annotations

from typing import Protocol

from documents.artifacts import DocumentArtifact
from documents.document_type import DocumentType


class DocumentTypeDetectionStrategy(Protocol):
    def resolve(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentType | None:
        ...
