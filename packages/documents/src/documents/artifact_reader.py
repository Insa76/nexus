from __future__ import annotations

from typing import Protocol

from documents.artifacts import DocumentArtifact


class ArtifactReader(Protocol):
    def read(self, artifact: DocumentArtifact) -> str:
        ...
