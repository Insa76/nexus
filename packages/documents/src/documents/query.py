from __future__ import annotations

from dataclasses import dataclass, field

from documents.context_relevance import DocumentContextMatch
from documents.models import Document


@dataclass(frozen=True)
class DocumentQueryResult:
    """
    Resultado de una consulta sobre documentos.

    `documents` contiene los documentos de la página actual.

    `total` representa la cantidad total de documentos encontrados
    antes de aplicar paginación.

    `query` conserva los parámetros utilizados para producir
    el resultado, permitiendo trazabilidad.

    `matches` conserva, cuando están disponibles, las relaciones
    de relevancia contextual asociadas a los documentos de la página.
    """

    documents: tuple[Document, ...]
    total: int
    query: dict[str, object] = field(default_factory=dict)
    matches: tuple[DocumentContextMatch, ...] = ()
    offset: int = 0
    limit: int | None = None

    @classmethod
    def from_documents(
        cls,
        documents: tuple[Document, ...],
        *,
        query: dict[str, object] | None = None,
        matches: tuple[DocumentContextMatch, ...] = (),
        total: int | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> DocumentQueryResult:
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")

        if limit is not None and limit < 0:
            raise ValueError("limit must be greater than or equal to zero")

        return cls(
            documents=documents,
            total=len(documents) if total is None else total,
            query=dict(query or {}),
            matches=matches,
            offset=offset,
            limit=limit,
        )

    @property
    def is_empty(self) -> bool:
        return not self.documents

    @property
    def has_results(self) -> bool:
        return bool(self.documents)

    @property
    def has_more(self) -> bool:
        return self.offset + len(self.documents) < self.total

    def ordered_matches(self) -> tuple[DocumentContextMatch, ...]:
        if not self.matches:
            return ()

        return tuple(
            sorted(
                self.matches,
                key=lambda match: match.relevance,
                reverse=True,
            )
        )

    def ordered_documents(self) -> tuple[Document, ...]:
        if not self.matches:
            return self.documents

        return tuple(
            match.document
            for match in self.ordered_matches()
        )
