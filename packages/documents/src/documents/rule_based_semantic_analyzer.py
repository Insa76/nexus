from __future__ import annotations

from documents.change import DocumentChange
from documents.semantic_analyzer import DocumentSemanticAnalyzer
from documents.semantic_change import DocumentSemanticChange


class RuleBasedSemanticAnalyzer(DocumentSemanticAnalyzer):
    def analyze(self, change: DocumentChange) -> DocumentSemanticChange:
        if change.change_type.value == "added":
            meaning = "Se agregó contenido al documento."
        elif change.change_type.value == "removed":
            meaning = "Se eliminó contenido del documento."
        else:
            meaning = "Se modificó contenido existente del documento."

        return DocumentSemanticChange(
            source_change=change,
            meaning=meaning,
            confidence=1.0,
        )
