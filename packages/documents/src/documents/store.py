from __future__ import annotations

from documents.models import Document


class DocumentStore:
    """
    Almacenamiento en memoria de documentos.
    """

    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}

    def add(self, document: Document) -> Document:
        self._documents[document.id] = document
        return document

    def get(self, document_id: str) -> Document | None:
        return self._documents.get(document_id)

    def list(self) -> list[Document]:
        return list(self._documents.values())

    def list_for_user(
        self,
        user_id: str,
    ) -> list[Document]:
        return [
            document
            for document in self._documents.values()
            if document.user_id == user_id
        ]

    def list_for_organization(
        self,
        organization_id: str,
    ) -> list[Document]:
        return [
            document
            for document in self._documents.values()
            if document.organization_id == organization_id
        ]

    def list_for_project(
        self,
        project_id: str,
    ) -> list[Document]:
        return [
            document
            for document in self._documents.values()
            if document.project_id == project_id
        ]

    def list_for_context(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> list[Document]:
        if (
            user_id is None
            and organization_id is None
            and project_id is None
        ):
            raise ValueError(
                "At least one document context filter is required"
            )

        return [
            document
            for document in self._documents.values()
            if (
                user_id is None
                or document.user_id == user_id
            )
            and (
                organization_id is None
                or document.organization_id == organization_id
            )
            and (
                project_id is None
                or document.project_id == project_id
            )
        ]

    def update(self, document: Document) -> Document:
        if document.id not in self._documents:
            raise KeyError(
                f"Document '{document.id}' not found"
            )

        self._documents[document.id] = document
        return document

    def remove(self, document_id: str) -> Document | None:
        return self._documents.pop(
            document_id,
            None,
        )

    def clear(self) -> None:
        self._documents.clear()

    def count(self) -> int:
        return len(self._documents)
