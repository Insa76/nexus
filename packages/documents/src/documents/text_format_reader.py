from __future__ import annotations

from documents.artifact_reader import ArtifactReader
from documents.artifacts import DocumentArtifact
from documents.document_type import DocumentType
from documents.format_reader import DocumentFormatReader


class TextFormatReader:
    """
    Reader especializado para documentos de texto plano.
    """

    def __init__(
        self,
        artifact_reader: ArtifactReader,
    ) -> None:
        self._artifact_reader = artifact_reader

    def supports(
        self,
        document_type: DocumentType,
    ) -> bool:
        return document_type.mime_type == "text/plain"

    def read(
        self,
        artifact: DocumentArtifact,
        document_type: DocumentType,
    ) -> str:
        if not self.supports(document_type):
            raise ValueError(
                "TextFormatReader does not support "
                f"{document_type.mime_type}"
            )

        return self._artifact_reader.read(
            artifact
        )
