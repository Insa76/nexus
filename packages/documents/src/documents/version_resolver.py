from __future__ import annotations

from dataclasses import dataclass

from documents.content_version import DocumentContentVersion
from documents.content_version_store import DocumentContentVersionStore


@dataclass(frozen=True)
class DocumentVersionResolution:
    document_id: str
    from_version: DocumentContentVersion
    to_version: DocumentContentVersion


class DocumentVersionResolver:
    def __init__(self, store: DocumentContentVersionStore):
        self.store = store

    def resolve_version(
        self,
        document_id: str,
        version: int,
    ) -> DocumentContentVersion:
        versions = self.store.list_for_document(document_id)

        for content_version in versions:
            if content_version.version == version:
                return content_version

        raise ValueError(
            f"Document content version not found: "
            f"{document_id} v{version}"
        )

    def resolve_latest(
        self,
        document_id: str,
    ) -> DocumentContentVersion:
        latest = self.store.get_latest_for_document(document_id)

        if latest is None:
            raise ValueError(
                f"No content versions found for document: {document_id}"
            )

        return latest

    def resolve_previous(
        self,
        document_id: str,
        version: int | None = None,
    ) -> DocumentContentVersion:
        versions = self.store.list_for_document(document_id)

        if not versions:
            raise ValueError(
                f"No content versions found for document: {document_id}"
            )

        target_version = (
            self.resolve_latest(document_id).version
            if version is None
            else version
        )

        previous = [
            content_version
            for content_version in versions
            if content_version.version < target_version
        ]

        if not previous:
            raise ValueError(
                f"No previous content version found for document: "
                f"{document_id} v{target_version}"
            )

        return max(previous, key=lambda item: item.version)

    def resolve_pair(
        self,
        document_id: str,
        from_version: int,
        to_version: int,
    ) -> DocumentVersionResolution:
        if from_version == to_version:
            raise ValueError(
                "Cannot resolve a version comparison pair with "
                "the same version"
            )

        from_content_version = self.resolve_version(
            document_id,
            from_version,
        )
        to_content_version = self.resolve_version(
            document_id,
            to_version,
        )

        return DocumentVersionResolution(
            document_id=document_id,
            from_version=from_content_version,
            to_version=to_content_version,
        )

    def resolve_latest_pair(
        self,
        document_id: str,
    ) -> DocumentVersionResolution:
        latest = self.resolve_latest(document_id)
        previous = self.resolve_previous(
            document_id,
            version=latest.version,
        )

        return DocumentVersionResolution(
            document_id=document_id,
            from_version=previous,
            to_version=latest,
        )
