from __future__ import annotations

from dataclasses import dataclass

from documents.context_access import DocumentContextAccess
from documents.query import DocumentQueryResult
from documents.context_relevance import DocumentContextMatch
from documents.models import Document


@dataclass(slots=True)
class DocumentCapability:
    """
    Interfaz cognitiva de acceso a documentos.

    Expone operaciones orientadas al Assistant/Cognitive Core
    sin exponer stores ni detalles internos del subsistema Documents.
    """

    context_access: DocumentContextAccess

    def query(
        self,
        *,
        context: object,
        name: str | None = None,
        mime_type: str | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> DocumentQueryResult:
        return self.context_access.query_from_context(
            context,
            name=name,
            mime_type=mime_type,
            offset=offset,
            limit=limit,
        )

    def relevant(
        self,
        *,
        context: object,
    ) -> tuple[DocumentContextMatch, ...]:
        return self.context_access.resolve_ordered_matches_from_context(
            context,
        )

    def relevant_documents(
        self,
        *,
        context: object,
    ) -> tuple[Document, ...]:
        return self.context_access.resolve_ordered_documents_from_context(
            context,
        )
