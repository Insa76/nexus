from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from documents.capability import DocumentCapability
from documents.models import Document
from documents.query import DocumentQueryResult


@dataclass(frozen=True, slots=True)
class DocumentCognitiveResult:
    """
    Resultado de una operación cognitiva sobre Documents.

    Representa información que el Cognitive Core puede utilizar
    para razonar sobre documentos sin conocer stores ni detalles
    internos del subsistema Documents.
    """

    query: DocumentQueryResult
    documents: tuple[Document, ...]
    metadata: dict[str, Any]


class DocumentCognitiveAccess:
    """
    Punto de acceso cognitivo a Documents.

    Esta capa traduce una necesidad cognitiva del Assistant
    en una operación sobre DocumentCapability.

    No conoce stores.
    No ejecuta acciones del Runtime.
    No interpreta lenguaje natural.
    """

    def __init__(
        self,
        capability: DocumentCapability,
    ) -> None:
        self._capability = capability

    def find_relevant(
        self,
        *,
        context: object,
        name: str | None = None,
        mime_type: str | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> DocumentCognitiveResult:
        query = self._capability.query(
            context=context,
            name=name,
            mime_type=mime_type,
            offset=offset,
            limit=limit,
        )

        documents = self._capability.relevant_documents(
            context=context,
        )

        return DocumentCognitiveResult(
            query=query,
            documents=documents,
            metadata={
                "operation": "find_relevant",
                "name": name,
                "mime_type": mime_type,
                "offset": offset,
                "limit": limit,
                "count": len(documents),
            },
        )
