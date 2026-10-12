from __future__ import annotations

from dataclasses import dataclass

from documents.change import DocumentChange


@dataclass(frozen=True)
class DocumentSemanticChange:
    source_change: DocumentChange
    meaning: str
    topics: tuple[str, ...] = ()
    impact: str | None = None
    confidence: float | None = None

    def __post_init__(self) -> None:
        if not self.meaning.strip():
            raise ValueError(
                "Semantic change meaning cannot be empty"
            )

        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Semantic change confidence must be between 0 and 1"
            )

        normalized_topics = tuple(
            topic.strip()
            for topic in self.topics
            if topic.strip()
        )

        object.__setattr__(
            self,
            "topics",
            normalized_topics,
        )

        if self.impact is not None:
            normalized_impact = self.impact.strip()

            object.__setattr__(
                self,
                "impact",
                normalized_impact or None,
            )
