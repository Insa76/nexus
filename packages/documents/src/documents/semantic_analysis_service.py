from __future__ import annotations

from documents.semantic_analysis import DocumentSemanticAnalysis
from documents.semantic_analyzer import DocumentSemanticAnalyzer
from documents.version_change import DocumentVersionChangeResult


class DocumentSemanticAnalysisService:
    def __init__(
        self,
        analyzer: DocumentSemanticAnalyzer,
    ):
        self.analyzer = analyzer

    def analyze(
        self,
        result: DocumentVersionChangeResult,
    ) -> DocumentSemanticAnalysis:
        semantic_changes = tuple(
            self.analyzer.analyze(change)
            for change in result.changes
        )

        return DocumentSemanticAnalysis(
            source=result,
            changes=semantic_changes,
        )
