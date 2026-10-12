from __future__ import annotations

from dataclasses import dataclass

from documents.semantic_change import DocumentSemanticChange


@dataclass(frozen=True)
class DocumentKnowledge:
    source_change: DocumentSemanticChange
    statement: str
    topic: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError(
                "Document knowledge statement cannot be empty"
            )

        if self.topic is not None:
            normalized_topic = self.topic.strip()
            object.__setattr__(
                self,
                "topic",
                normalized_topic or None,
            )

        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Document knowledge confidence must be between 0 and 1"
            )
