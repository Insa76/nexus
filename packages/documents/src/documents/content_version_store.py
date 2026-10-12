from __future__ import annotations

from documents.content_version import DocumentContentVersion


class DocumentContentVersionStore:
    def __init__(self) -> None:
        self._versions: dict[str, DocumentContentVersion] = {}

    def add(
        self,
        version: DocumentContentVersion,
    ) -> DocumentContentVersion:
        self._versions[version.id] = version
        return version

    def get(
        self,
        version_id: str,
    ) -> DocumentContentVersion | None:
        return self._versions.get(version_id)

    def list(self) -> list[DocumentContentVersion]:
        return list(self._versions.values())

    def list_for_document(
        self,
        document_id: str,
    ) -> list[DocumentContentVersion]:
        return [
            version
            for version in self._versions.values()
            if version.document_id == document_id
        ]

    def get_latest_for_document(
        self,
        document_id: str,
    ) -> DocumentContentVersion | None:
        versions = self.list_for_document(document_id)

        if not versions:
            return None

        return max(
            versions,
            key=lambda version: version.version,
        )

    def get_next_version(
        self,
        document_id: str,
    ) -> int:
        latest = self.get_latest_for_document(
            document_id
        )

        if latest is None:
            return 1

        return latest.version + 1

    def remove(
        self,
        version_id: str,
    ) -> DocumentContentVersion | None:
        return self._versions.pop(version_id, None)

    def remove_for_document(
        self,
        document_id: str,
    ) -> int:
        versions = [
            version
            for version in self._versions.values()
            if version.document_id == document_id
        ]

        for version in versions:
            self._versions.pop(version.id, None)

        return len(versions)

    def clear(self) -> None:
        self._versions.clear()

    def count(self) -> int:
        return len(self._versions)
