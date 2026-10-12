from __future__ import annotations

from documents.artifacts import DocumentArtifact
from documents.document_type import DocumentType


class DeclaredTypeDetectionStrategy:
    def __init__(
        self,
        declared_types: dict[str, str] | None = None,
    ) -> None:
        self._declared_types = dict(
            declared_types or {}
        )

    def resolve(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentType | None:
        mime_type = self._declared_types.get(
            artifact.id
        )

        if mime_type is None:
            return None

        return DocumentType.from_mime_type(
            mime_type
        )

    def declare(
        self,
        artifact: DocumentArtifact,
        mime_type: str,
    ) -> None:
        self._declared_types[
            artifact.id
        ] = mime_type

    def remove(
        self,
        artifact: DocumentArtifact,
    ) -> str | None:
        return self._declared_types.pop(
            artifact.id,
            None,
        )
