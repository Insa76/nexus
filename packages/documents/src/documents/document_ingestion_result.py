from __future__ import annotations

from dataclasses import dataclass

from documents.resolver import DocumentResolution
from documents.type_detection_evidence import (
    DocumentTypeDetectionEvidence,
)
from documents.type_validation import DocumentTypeValidation


@dataclass(frozen=True)
class DocumentIngestionResult:
    resolution: DocumentResolution
    type_validation: DocumentTypeValidation | None = None
    detection_evidence: DocumentTypeDetectionEvidence | None = None

    @property
    def document(self):
        return self.resolution.document

    @property
    def artifact(self):
        return self.resolution.artifact

    @property
    def content(self):
        return self.resolution.content

    @property
    def type_matches(self) -> bool | None:
        if self.type_validation is None:
            return None

        return self.type_validation.matches

    @property
    def type_mismatch(self) -> bool | None:
        if self.type_validation is None:
            return None

        return self.type_validation.mismatch

    @property
    def detected_type(self):
        if self.detection_evidence is None:
            return None

        return self.detection_evidence.detected_type

    @property
    def detection_strategy(self) -> str | None:
        if self.detection_evidence is None:
            return None

        return self.detection_evidence.strategy
