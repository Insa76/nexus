from __future__ import annotations

from documents.knowledge_extraction import DocumentKnowledgeExtraction
from documents.knowledge_extractor import DocumentKnowledgeExtractor
from documents.semantic_analysis import DocumentSemanticAnalysis


class DocumentKnowledgeExtractionService:
    def __init__(
        self,
        extractor: DocumentKnowledgeExtractor,
    ):
        self.extractor = extractor

    def extract(
        self,
        analysis: DocumentSemanticAnalysis,
    ) -> DocumentKnowledgeExtraction:
        knowledge = tuple(
            item
            for change in analysis.changes
            for item in self.extractor.extract(change)
        )

        return DocumentKnowledgeExtraction(
            source=analysis,
            knowledge=knowledge,
        )
