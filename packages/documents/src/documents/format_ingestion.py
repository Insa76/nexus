from __future__ import annotations

from dataclasses import dataclass

from documents.artifact_type_resolver import ArtifactTypeResolver
from documents.artifacts import DocumentArtifact
from documents.content import DocumentContent
from documents.document_type import DocumentType
from documents.format_reader_registry import FormatReaderRegistry
from documents.ingestion import IngestionResult
from documents.type_detection_evidence import (
    DocumentTypeDetectionEvidence,
)
from documents.type_validation import DocumentTypeValidation
from documents.type_validator import DocumentTypeValidator


@dataclass(frozen=True)
class FormatIngestionResult:
    ingestion: IngestionResult
    type_validation: DocumentTypeValidation | None = None
    detection_evidence: DocumentTypeDetectionEvidence | None = None


class FormatIngestionService:
    def __init__(
        self,
        reader_registry: FormatReaderRegistry,
        type_resolver: ArtifactTypeResolver | None = None,
        type_validator: DocumentTypeValidator | None = None,
    ) -> None:
        self._reader_registry = reader_registry
        self._type_resolver = (
            type_resolver
            if type_resolver is not None
            else ArtifactTypeResolver()
        )
        self._type_validator = (
            type_validator
            if type_validator is not None
            else DocumentTypeValidator()
        )

    def ingest(
        self,
        artifact: DocumentArtifact,
        document_type: str | DocumentType | None = None,
    ) -> IngestionResult:
        resolved_type = self._resolve_type(
            artifact=artifact,
            document_type=document_type,
        )

        reader = self._reader_registry.get(
            resolved_type
        )

        if reader is None:
            raise ValueError(
                "No format reader registered for content type: "
                f"{resolved_type.mime_type}"
            )

        text = reader.read(
            artifact,
            resolved_type,
        )

        content = DocumentContent.create(
            text=text,
            content_type=resolved_type.mime_type,
        )

        return IngestionResult(
            artifact=artifact,
            content=content,
        )

    def ingest_with_validation(
        self,
        artifact: DocumentArtifact,
        declared_type: str | DocumentType,
    ) -> FormatIngestionResult:
        detection_evidence = (
            self._type_resolver.resolve_with_evidence(
                artifact
            )
        )

        validation = self._type_validator.validate(
            declared_type=declared_type,
            detected_type=detection_evidence.detected_type,
        )

        ingestion = self.ingest(
            artifact=artifact,
            document_type=detection_evidence.detected_type,
        )

        return FormatIngestionResult(
            ingestion=ingestion,
            type_validation=validation,
            detection_evidence=detection_evidence,
        )

    def _resolve_type(
        self,
        artifact: DocumentArtifact,
        document_type: str | DocumentType | None,
    ) -> DocumentType:
        if isinstance(
            document_type,
            DocumentType,
        ):
            return document_type

        if isinstance(
            document_type,
            str,
        ):
            return DocumentType.from_mime_type(
                document_type
            )

        return self._type_resolver.resolve(
            artifact
        )

    def supported_content_types(self) -> list[str]:
        return self._reader_registry.content_types()
