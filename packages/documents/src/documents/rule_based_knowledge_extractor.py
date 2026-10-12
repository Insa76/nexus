from __future__ import annotations

from documents.knowledge import DocumentKnowledge
from documents.semantic_change import DocumentSemanticChange
from documents.knowledge_extractor import DocumentKnowledgeExtractor


class RuleBasedDocumentKnowledgeExtractor(
    DocumentKnowledgeExtractor
):
    def extract(
        self,
        change: DocumentSemanticChange,
    ) -> tuple[DocumentKnowledge, ...]:
        return (
            DocumentKnowledge(
                source_change=change,
                statement=change.meaning,
                topic=(
                    change.topics[0]
                    if change.topics
                    else None
                ),
                confidence=change.confidence,
            ),
        )
