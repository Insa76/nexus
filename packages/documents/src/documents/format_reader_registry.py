from __future__ import annotations

from documents.document_type import DocumentType
from documents.format_reader import DocumentFormatReader


class FormatReaderRegistry:
    def __init__(self) -> None:
        self._readers: dict[str, DocumentFormatReader] = {}

    @staticmethod
    def _normalize_document_type(
        document_type: str | DocumentType,
    ) -> str:
        if isinstance(document_type, DocumentType):
            return document_type.mime_type

        return DocumentType.from_mime_type(
            document_type
        ).mime_type

    def register(
        self,
        document_type: str | DocumentType,
        reader: DocumentFormatReader,
    ) -> None:
        normalized_type = self._normalize_document_type(
            document_type
        )

        self._readers[normalized_type] = reader

    def get(
        self,
        document_type: str | DocumentType,
    ) -> DocumentFormatReader | None:
        normalized_type = self._normalize_document_type(
            document_type
        )

        return self._readers.get(
            normalized_type
        )

    def supports(
        self,
        document_type: str | DocumentType,
    ) -> bool:
        normalized_type = self._normalize_document_type(
            document_type
        )

        return normalized_type in self._readers

    def remove(
        self,
        document_type: str | DocumentType,
    ) -> DocumentFormatReader | None:
        normalized_type = self._normalize_document_type(
            document_type
        )

        return self._readers.pop(
            normalized_type,
            None,
        )

    def clear(self) -> None:
        self._readers.clear()

    def content_types(self) -> list[str]:
        return list(self._readers)
