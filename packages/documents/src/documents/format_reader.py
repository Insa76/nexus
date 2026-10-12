from __future__ import annotations

from typing import Protocol

from documents.artifacts import DocumentArtifact
from documents.document_type import DocumentType


class DocumentFormatReader(Protocol):
    """
    Lee e interpreta un artifact según su formato documental.

    A diferencia de ArtifactReader, que solamente obtiene
    el contenido físico, este componente conoce el formato
    del documento.
    """

    def supports(
        self,
        document_type: DocumentType,
    ) -> bool:
        ...

    def read(
        self,
        artifact: DocumentArtifact,
        document_type: DocumentType,
    ) -> str:
        ...
