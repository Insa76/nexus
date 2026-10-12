from __future__ import annotations

from dataclasses import dataclass

from documents.version_resolver import DocumentVersionResolution


@dataclass(frozen=True)
class DocumentVersionComparison:
    document_id: str
    from_version: int
    to_version: int
    from_content_id: str
    to_content_id: str
    changed: bool

    @property
    def unchanged(self) -> bool:
        return not self.changed


class DocumentVersionComparator:
    def compare(
        self,
        resolution: DocumentVersionResolution,
    ) -> DocumentVersionComparison:
        from_version = resolution.from_version
        to_version = resolution.to_version

        changed = from_version.content_id != to_version.content_id

        return DocumentVersionComparison(
            document_id=resolution.document_id,
            from_version=from_version.version,
            to_version=to_version.version,
            from_content_id=from_version.content_id,
            to_content_id=to_version.content_id,
            changed=changed,
        )
