from __future__ import annotations

from dataclasses import dataclass

from documents.change import DocumentChange
from documents.version_comparison import DocumentVersionComparison


@dataclass(frozen=True)
class DocumentVersionChangeResult:
    comparison: DocumentVersionComparison
    changes: tuple[DocumentChange, ...]

    @property
    def changed(self) -> bool:
        return bool(self.changes)

    @property
    def unchanged(self) -> bool:
        return not self.changed
