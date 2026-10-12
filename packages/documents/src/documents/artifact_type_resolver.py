from __future__ import annotations

from documents.artifacts import DocumentArtifact
from documents.declared_type_detection import DeclaredTypeDetectionStrategy
from documents.extension_type_detection import ExtensionTypeDetectionStrategy
from documents.type_detection import DocumentTypeDetectionStrategy
from documents.type_detection_evidence import DocumentTypeDetectionEvidence
from documents.document_type import DocumentType


class ArtifactTypeResolver:
    def __init__(
        self,
        strategies: list[DocumentTypeDetectionStrategy] | None = None,
    ) -> None:
        self._strategies = list(
            strategies
            if strategies is not None
            else [
                DeclaredTypeDetectionStrategy(),
                ExtensionTypeDetectionStrategy(),
            ]
        )

    def resolve(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentType:
        evidence = self.resolve_with_evidence(
            artifact
        )

        return evidence.detected_type

    def resolve_with_evidence(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentTypeDetectionEvidence:
        for strategy in self._strategies:
            detected_type = strategy.resolve(
                artifact
            )

            if detected_type is not None:
                return DocumentTypeDetectionEvidence(
                    detected_type=detected_type,
                    strategy=type(strategy).__name__,
                )

        raise ValueError(
            "Cannot resolve document type for artifact: "
            f"{artifact.id}"
        )

    def strategies(
        self,
    ) -> list[DocumentTypeDetectionStrategy]:
        return list(self._strategies)
