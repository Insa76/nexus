from __future__ import annotations

from pathlib import Path

from documents.artifacts import DocumentArtifact
from documents.document_type import DocumentType


class ExtensionTypeDetectionStrategy:
    _EXTENSION_TYPES: dict[str, str] = {
        ".txt": "text/plain",
        ".text": "text/plain",
        ".md": "text/markdown",
        ".markdown": "text/markdown",
        ".csv": "text/csv",
        ".json": "application/json",
        ".pdf": "application/pdf",
        ".html": "text/html",
        ".htm": "text/html",
    }

    def resolve(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentType | None:
        location = artifact.location.strip()

        if not location:
            return None

        extension = Path(location).suffix.lower()

        mime_type = self._EXTENSION_TYPES.get(
            extension
        )

        if mime_type is None:
            return None

        return DocumentType.from_mime_type(
            mime_type
        )
