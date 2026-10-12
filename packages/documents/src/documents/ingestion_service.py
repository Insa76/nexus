from __future__ import annotations

from documents.artifacts import DocumentArtifact
from documents.document_type import DocumentType
from documents.ingestion import IngestionResult
from documents.ingestion_registry import IngestionRegistry
from documents.type_resolver import DocumentTypeResolver


class DocumentIngestionService:
    def __init__(
        self,
        registry: IngestionRegistry,
        type_resolver: DocumentTypeResolver | None = None,
    ) -> None:
        self._registry = registry
        self._type_resolver = (
            type_resolver
            if type_resolver is not None
            else DocumentTypeResolver()
        )

    def ingest(
        self,
        artifact: DocumentArtifact,
        content_type: str | DocumentType,
    ) -> IngestionResult:
        document_type = (
            content_type
            if isinstance(content_type, DocumentType)
            else self._type_resolver.resolve(content_type)
        )

        ingestor = self._registry.get(
            document_type.mime_type
        )

        if ingestor is None:
            raise ValueError(
                "No ingestor registered for content type: "
                f"{document_type.mime_type}"
            )

        return ingestor.ingest(
            artifact
        )

    def supported_content_types(self) -> list[str]:
        """
        Devuelve los tipos MIME normalizados para los cuales
        existe un ingestor registrado.
        """

        return self._registry.content_types()
