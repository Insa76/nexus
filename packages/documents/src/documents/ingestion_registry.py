from __future__ import annotations

from documents.document_type import DocumentType
from documents.ingestion import DocumentIngestor


class IngestionRegistry:
    def __init__(self) -> None:
        self._ingestors: dict[str, DocumentIngestor] = {}

    @staticmethod
    def _normalize_content_type(
        content_type: str | DocumentType,
    ) -> str:
        if isinstance(content_type, DocumentType):
            return content_type.mime_type

        return DocumentType.from_mime_type(
            content_type
        ).mime_type

    def register(
        self,
        content_type: str | DocumentType,
        ingestor: DocumentIngestor,
    ) -> None:
        normalized_type = self._normalize_content_type(
            content_type
        )

        self._ingestors[normalized_type] = ingestor

    def get(
        self,
        content_type: str | DocumentType,
    ) -> DocumentIngestor | None:
        normalized_type = self._normalize_content_type(
            content_type
        )

        return self._ingestors.get(
            normalized_type
        )

    def supports(
        self,
        content_type: str | DocumentType,
    ) -> bool:
        normalized_type = self._normalize_content_type(
            content_type
        )

        return normalized_type in self._ingestors

    def remove(
        self,
        content_type: str | DocumentType,
    ) -> DocumentIngestor | None:
        normalized_type = self._normalize_content_type(
            content_type
        )

        return self._ingestors.pop(
            normalized_type,
            None,
        )

    def clear(self) -> None:
        self._ingestors.clear()

    def content_types(self) -> list[str]:
        return list(
            self._ingestors
        )
