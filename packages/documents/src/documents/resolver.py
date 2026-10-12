from __future__ import annotations

from dataclasses import dataclass

from documents.artifact_store import ArtifactStore
from documents.artifacts import DocumentArtifact
from documents.content import DocumentContent
from documents.content_store import ContentStore
from documents.models import Document
from documents.store import DocumentStore


@dataclass(frozen=True)
class DocumentResolution:
    document: Document
    artifact: DocumentArtifact | None
    content: DocumentContent | None


class DocumentResolver:
    def __init__(
        self,
        document_store: DocumentStore,
        artifact_store: ArtifactStore,
        content_store: ContentStore | None = None,
    ) -> None:
        self._document_store = document_store
        self._artifact_store = artifact_store
        self._content_store = content_store

    def resolve(self, document_id: str) -> DocumentResolution | None:
        document = self._document_store.get(document_id)

        if document is None:
            return None

        artifact = None
        if document.artifact_id is not None:
            artifact = self._artifact_store.get(document.artifact_id)

        content = None
        if self._content_store is not None and document.content_id is not None:
            content = self._content_store.get(document.content_id)

        return DocumentResolution(
            document=document,
            artifact=artifact,
            content=content,
        )
