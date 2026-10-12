from __future__ import annotations

from dataclasses import dataclass

from documents.knowledge import DocumentKnowledge
from documents.semantic_analysis import DocumentSemanticAnalysis


@dataclass(frozen=True)
class DocumentKnowledgeExtraction:
    source: DocumentSemanticAnalysis
    knowledge: tuple[DocumentKnowledge, ...]

    @property
    def extracted(self) -> bool:
        return bool(self.knowledge)

    @property
    def empty(self) -> bool:
        return not self.extracted
