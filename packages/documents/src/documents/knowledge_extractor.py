from __future__ import annotations

from typing import Protocol, runtime_checkable

from documents.knowledge import DocumentKnowledge
from documents.semantic_change import DocumentSemanticChange


@runtime_checkable
class DocumentKnowledgeExtractor(Protocol):
    def extract(
        self,
        change: DocumentSemanticChange,
    ) -> tuple[DocumentKnowledge, ...]:
        ...
