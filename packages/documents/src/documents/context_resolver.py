from __future__ import annotations

from dataclasses import dataclass

from context import project_ids_for_context
from documents.access import DocumentsAccess
from documents.context_relevance import (
    DocumentContextMatch,
)
from documents.context_relevance_resolver import (
    DocumentContextRelevanceResolver,
)
from documents.models import Document
from documents.query import DocumentQueryResult


@dataclass(frozen=True)
class DocumentContextSelection:
    """
    Selección contextual utilizada para resolver documentos.
    """

    user_id: str | None = None
    organization_id: str | None = None
    project_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocumentContext:
    """
    Documentos relevantes para un contexto operativo.

    La selección que originó los documentos queda preservada
    para mantener trazabilidad.

    `documents` se mantiene como acceso directo compatible.
    `matches` agrega la relevancia contextual de cada documento.
    """

    selection: DocumentContextSelection
    documents: tuple[Document, ...]
    matches: tuple[DocumentContextMatch, ...]

    @classmethod
    def empty(
        cls,
        selection: DocumentContextSelection,
    ) -> DocumentContext:
        return cls(
            selection=selection,
            documents=(),
            matches=(),
        )

    def ordered_matches(
        self,
    ) -> tuple[DocumentContextMatch, ...]:
        return tuple(
            sorted(
                self.matches,
                key=lambda match: match.relevance,
                reverse=True,
            )
        )

    def ordered_documents(self) -> tuple[Document, ...]:
        return tuple(
            match.document
            for match in self.ordered_matches()
        )

    def documents_by_mime_type(
        self,
        mime_type: str,
    ) -> tuple[Document, ...]:
        return tuple(
            document
            for document in self.documents
            if document.mime_type == mime_type
        )

    def documents_by_name(
        self,
        name: str,
    ) -> tuple[Document, ...]:
        normalized_name = name.strip().lower()

        return tuple(
            document
            for document in self.documents
            if normalized_name in document.name.lower()
        )

    def filter(
        self,
        *,
        name: str | None = None,
        mime_type: str | None = None,
    ) -> tuple[Document, ...]:
        normalized_name = (
            name.strip().lower()
            if name is not None
            else None
        )

        return tuple(
            document
            for document in self.documents
            if (
                normalized_name is None
                or normalized_name in document.name.lower()
            )
            and (
                mime_type is None
                or document.mime_type == mime_type
            )
        )

    def query(
        self,
        *,
        name: str | None = None,
        mime_type: str | None = None,
        offset: int = 0,
        limit: int | None = None,
    ) -> DocumentQueryResult:
        normalized_name = (
            name.strip().lower()
            if name is not None
            else None
        )

        if offset < 0:
            raise ValueError(
                "offset must be greater than or equal to zero"
            )

        if limit is not None and limit < 0:
            raise ValueError(
                "limit must be greater than or equal to zero"
            )

        matched_documents = tuple(
            match.document
            for match in self.matches
            if (
                normalized_name is None
                or normalized_name in match.document.name.lower()
            )
            and (
                mime_type is None
                or match.document.mime_type == mime_type
            )
        )

        matched_document_ids = {
            document.id
            for document in matched_documents
        }

        matches = tuple(
            match
            for match in self.matches
            if match.document.id in matched_document_ids
        )

        total = len(matched_documents)

        if limit is None:
            paginated_documents = matched_documents[offset:]
            paginated_ids = {
                document.id
                for document in paginated_documents
            }
        else:
            paginated_documents = matched_documents[
             offset:offset + limit
            ]
            paginated_ids = {
                document.id
                for document in paginated_documents
            }

        paginated_matches = tuple(
            match
            for match in matches
            if match.document.id in paginated_ids
        )

        return DocumentQueryResult.from_documents(
            paginated_documents,
            total=total,
            offset=offset,
            limit=limit,
            query={
    key: value
    for key, value in {
        "name": name,
        "mime_type": mime_type,
        "offset": offset if offset != 0 else None,
        "limit": limit,
    }.items()
    if value is not None
},
            matches=paginated_matches,
        )

class DocumentContextResolver:
    """
    Resuelve documentos relevantes para un contexto operativo.

    No conoce AssistantContext, ContextStore ni Engine.
    """

    def __init__(
        self,
        access: DocumentsAccess,
        relevance_resolver: DocumentContextRelevanceResolver | None = None,
    ) -> None:
        self._access = access
        self._relevance_resolver = (
            relevance_resolver
            or DocumentContextRelevanceResolver()
        )

    def resolve(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_ids: tuple[str, ...] = (),
    ) -> DocumentContext:
        selection = DocumentContextSelection(
            user_id=user_id,
            organization_id=organization_id,
            project_ids=tuple(project_ids),
        )

        if not user_id and not organization_id and not project_ids:
            return DocumentContext.empty(selection)

        # ---------------------------------------------------------
        # DOCUMENTS
        # ---------------------------------------------------------
        #
        # `documents` mantiene la semántica de resolución
        # contextual exacta.
        #
        # Cuando hay proyectos explícitos:
        #
        #   USER + ORGANIZATION + PROJECT
        #
        # Cuando no hay proyectos:
        #
        #   USER + ORGANIZATION
        #
        # Los resultados se deduplican preservando el orden.
        #

        documents: list[Document] = []

        if project_ids:
            for project_id in project_ids:
                documents.extend(
                    self._access.list_documents_for_context(
                        user_id=user_id,
                        organization_id=organization_id,
                        project_id=project_id,
                    )
                )
        else:
            if user_id is not None:
                documents.extend(
                    self._access.list_documents_for_context(
                        user_id=user_id,
                    )
                )

            if organization_id is not None:
                documents.extend(
                    self._access.list_documents_for_context(
                        organization_id=organization_id,
                    )
                )

        unique_documents: list[Document] = []

        for document in documents:
            if document not in unique_documents:
                unique_documents.append(document)

        # ---------------------------------------------------------
        # MATCH DOCUMENTS
        # ---------------------------------------------------------
        #
        # Para calcular relevancia necesitamos considerar todos
        # los niveles del contexto:
        #
        #   USER
        #   ORGANIZATION
        #   PROJECT
        #
        # Esto es deliberadamente diferente de `documents`.
        #
        # `documents` representa la resolución documental.
        # `matches` representa la clasificación contextual.
        #

        match_documents: list[Document] = []

        if user_id is not None:
            match_documents.extend(
                self._access.list_documents_for_context(
                    user_id=user_id,
                )
            )

        if organization_id is not None:
            match_documents.extend(
                self._access.list_documents_for_context(
                    organization_id=organization_id,
                )
            )

        for project_id in project_ids:
            match_documents.extend(
                self._access.list_documents_for_context(
                    project_id=project_id,
                )
            )

        unique_match_documents: list[Document] = []

        for document in match_documents:
            if document not in unique_match_documents:
                unique_match_documents.append(document)

        # ---------------------------------------------------------
        # RELEVANCE MATCHES
        # ---------------------------------------------------------

        matches = tuple(
            match
            for document in unique_match_documents
            if (
                match := self._relevance_resolver.resolve(
                    document=document,
                    selection=selection,
                )
            )
            is not None
        )

        return DocumentContext(
            selection=selection,
            documents=tuple(unique_documents),
            matches=matches,
        )

    def resolve_from_context(
        self,
        context,
    ) -> DocumentContext:
        user_id = (
            context.user.id
            if context.user is not None
            else None
        )

        organization_id = (
            context.organization.id
            if context.organization is not None
            else None
        )

        project_ids = tuple(
            project_id
            for project_id in project_ids_for_context(context)
        )

        if (
            user_id is None
            and organization_id is None
            and not project_ids
        ):
            return DocumentContext.empty(
                DocumentContextSelection()
            )

        return self.resolve(
            user_id=user_id,
            organization_id=organization_id,
            project_ids=project_ids,
        )
