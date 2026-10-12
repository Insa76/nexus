from __future__ import annotations

from dataclasses import dataclass

from documents.semantic_change import DocumentSemanticChange
from documents.version_change import DocumentVersionChangeResult


@dataclass(frozen=True)
class DocumentSemanticAnalysis:
    source: DocumentVersionChangeResult
    changes: tuple[DocumentSemanticChange, ...]

    @property
    def changed(self) -> bool:
        return bool(self.changes)

    @property
    def unchanged(self) -> bool:
        return not self.changed
