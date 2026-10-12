from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from documents.models import Document


class DocumentContextRelevance(IntEnum):
    USER = 1
    ORGANIZATION = 2
    PROJECT = 3


@dataclass(frozen=True)
class DocumentContextMatch:
    document: Document
    relevance: DocumentContextRelevance
