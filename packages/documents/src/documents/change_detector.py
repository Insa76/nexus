from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from documents.change import DocumentChange
from documents.version_comparison import DocumentVersionComparison


@dataclass(frozen=True)
class DocumentChangeDetection:
    comparison: DocumentVersionComparison
    changes: tuple[DocumentChange, ...]

    @property
    def changed(self) -> bool:
        return bool(self.changes)

    @property
    def unchanged(self) -> bool:
        return not self.changed


class DocumentChangeDetector:
    def detect(
        self,
        comparison: DocumentVersionComparison,
        before_text: str,
        after_text: str,
    ) -> DocumentChangeDetection:
        matcher = SequenceMatcher(
            a=before_text.splitlines(),
            b=after_text.splitlines(),
            autojunk=False,
        )

        changes: list[DocumentChange] = []

        before_lines = before_text.splitlines()
        after_lines = after_text.splitlines()

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == "equal":
                continue

            removed_lines = before_lines[i1:i2]
            added_lines = after_lines[j1:j2]

            if removed_lines and added_lines:
                common_count = min(
                    len(removed_lines),
                    len(added_lines),
                )

                for offset in range(common_count):
                    changes.append(
                        DocumentChange.modified(
                            before=removed_lines[offset],
                            after=added_lines[offset],
                            before_line=i1 + offset + 1,
                            after_line=j1 + offset + 1,
                        )
                    )

                for offset in range(
                    common_count,
                    len(removed_lines),
                ):
                    changes.append(
                        DocumentChange.removed(
                            removed_lines[offset],
                            line=i1 + offset + 1,
                        )
                    )

                for offset in range(
                    common_count,
                    len(added_lines),
                ):
                    changes.append(
                        DocumentChange.added(
                            added_lines[offset],
                            line=j1 + offset + 1,
                        )
                    )

            elif removed_lines:
                for offset, line in enumerate(removed_lines):
                    changes.append(
                        DocumentChange.removed(
                            line,
                            line=i1 + offset + 1,
                        )
                    )

            elif added_lines:
                for offset, line in enumerate(added_lines):
                    changes.append(
                        DocumentChange.added(
                            line,
                            line=j1 + offset + 1,
                        )
                    )

        return DocumentChangeDetection(
            comparison=comparison,
            changes=tuple(changes),
        )
