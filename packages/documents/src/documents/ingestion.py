from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from documents.artifacts import DocumentArtifact
from documents.content import DocumentContent


@dataclass(frozen=True)
class IngestionResult:
    artifact: DocumentArtifact
    content: DocumentContent


class DocumentIngestor(Protocol):
    def ingest(self, artifact: DocumentArtifact) -> IngestionResult:
        ...
