from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DocumentChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"


@dataclass(frozen=True)
class DocumentChange:
    change_type: DocumentChangeType
    before: str | None
    after: str | None
    before_line: int | None = None
    after_line: int | None = None

    @classmethod
    def added(
        cls,
        text: str,
        *,
        line: int | None = None,
    ) -> DocumentChange:
        return cls(
            change_type=DocumentChangeType.ADDED,
            before=None,
            after=text,
            before_line=None,
            after_line=line,
        )

    @classmethod
    def removed(
        cls,
        text: str,
        *,
        line: int | None = None,
    ) -> DocumentChange:
        return cls(
            change_type=DocumentChangeType.REMOVED,
            before=text,
            after=None,
            before_line=line,
            after_line=None,
        )

    @classmethod
    def modified(
        cls,
        before: str,
        after: str,
        *,
        before_line: int | None = None,
        after_line: int | None = None,
    ) -> DocumentChange:
        return cls(
            change_type=DocumentChangeType.MODIFIED,
            before=before,
            after=after,
            before_line=before_line,
            after_line=after_line,
        )
