from __future__ import annotations

from documents.artifact_reader import ArtifactReader
from documents.artifacts import DocumentArtifact
from documents.content import DocumentContent
from documents.ingestion import IngestionResult


class TextIngestor:
    def __init__(self, reader: ArtifactReader) -> None:
        self._reader = reader

    def ingest(self, artifact: DocumentArtifact) -> IngestionResult:
        text = self._reader.read(artifact)

        content = DocumentContent.create(
            text=text,
            content_type="text/plain",
        )

        return IngestionResult(
            artifact=artifact,
            content=content,
        )
