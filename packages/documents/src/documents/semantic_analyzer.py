from __future__ import annotations

from typing import Protocol, runtime_checkable

from documents.change import DocumentChange
from documents.semantic_change import DocumentSemanticChange


@runtime_checkable
class DocumentSemanticAnalyzer(Protocol):
    def analyze(self, change: DocumentChange) -> DocumentSemanticChange:
        ...
