from __future__ import annotations

from typing import TYPE_CHECKING

from documents.context_relevance import (
    DocumentContextMatch,
    DocumentContextRelevance,
)
from documents.models import Document

if TYPE_CHECKING:
    from documents.context_resolver import DocumentContextSelection


class DocumentContextRelevanceResolver:
    """
    Determina el nivel de especificidad contextual de un documento.

    No decide si un documento debe formar parte del contexto.
    Solamente clasifica el vínculo existente.
    """

    def resolve(
        self,
        *,
        document: Document,
        selection: DocumentContextSelection,
    ) -> DocumentContextMatch | None:
        if (
            document.project_id is not None
            and document.project_id in selection.project_ids
        ):
            return DocumentContextMatch(
                document=document,
                relevance=DocumentContextRelevance.PROJECT,
            )

        if (
            document.organization_id is not None
            and document.organization_id == selection.organization_id
        ):
            return DocumentContextMatch(
                document=document,
                relevance=DocumentContextRelevance.ORGANIZATION,
            )

        if (
            document.user_id is not None
            and document.user_id == selection.user_id
        ):
            return DocumentContextMatch(
                document=document,
                relevance=DocumentContextRelevance.USER,
            )

        return None
