from __future__ import annotations

from dataclasses import dataclass

from documents.artifacts import DocumentArtifact
from documents.document_ingestion_result import DocumentIngestionResult
from documents.models import Document
from documents.resolver import DocumentResolution
from documents.service import DocumentService
from documents.content import DocumentContent
from documents.content_version import DocumentContentVersion


@dataclass(slots=True)
class DocumentsAccess:
    service: DocumentService

    def create_document(
        self,
        *,
        name: str,
        mime_type: str,
        source: str,
        description: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
        artifact_id: str | None = None,
        content_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> Document:
        return self.service.create_document(
            name=name,
            mime_type=mime_type,
            source=source,
            description=description,
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
            artifact_id=artifact_id,
            content_id=content_id,
            metadata=metadata,
        )

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:
        return self.service.get_document(
            document_id,
        )

    def update_document(
        self,
        document: Document,
    ) -> Document:
        return self.service.update_document(
            document,
        )

    def get_artifact(
        self,
        artifact_id: str,
    ) -> DocumentArtifact | None:
        return self.service.get_artifact(
            artifact_id,
        )

    def get_content(
        self,
        content_id: str,
    ) -> DocumentContent | None:
        return self.service.get_content(
            content_id,
        )

    def count_documents(self) -> int:
        return self.service.count_documents()

    def list_documents(self) -> list[Document]:
        return self.service.list_documents()

    def remove_document(
        self,
        document_id: str,
    ):
        return self.service.remove_document(
            document_id
        )

    def add_artifact(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentArtifact:
        return self.service.add_artifact(
            artifact
        )

    def ingest(
        self,
        document: Document,
    ) -> DocumentResolution:
        return self.service.ingest(
            document
        )

    def ingest_with_validation(
        self,
        document: Document,
    ) -> DocumentIngestionResult:
        return self.service.ingest_with_validation(
            document
        )

    def resolve(
        self,
        document_id: str,
    ) -> DocumentResolution | None:
        return self.service.resolve(
            document_id
        )

    def supported_content_types(self) -> list[str]:
        return (
            self.service.ingestion_service
            .supported_content_types()
        )

    def list_knowledge_history(
        self,
        document_id: str,
    ):
        return self.service.list_knowledge_history(
            document_id
        )

    def list_latest_knowledge(
        self,
        document_id: str,
    ):
        return self.service.list_latest_knowledge(
            document_id
        )

    def list_knowledge_for_version(
        self,
        document_id: str,
        version: int,
    ):
        return self.service.list_knowledge_for_version(
            document_id=document_id,
            version=version,
        )

    def list_versions(
        self,
        document_id: str,
    ) -> list[DocumentContentVersion]:
        return self.service.list_versions(
            document_id,
        )

    def get_version(
        self,
        version_id: str,
    ) -> DocumentContentVersion | None:
        return self.service.get_version(
            version_id,
        )

    def get_latest_version(
        self,
        document_id: str,
    ) -> DocumentContentVersion | None:
        return self.service.get_latest_version(
            document_id,
        )

    def has_latest_knowledge(
        self,
        document_id: str,
    ) -> bool:
        return self.service.has_latest_knowledge(
            document_id,
        )

    def knowledge_count(
        self,
        document_id: str,
    ) -> int:
        return self.service.knowledge_count(
            document_id,
        )

    def validate_latest_knowledge(
        self,
        document_id: str,
    ) -> bool:
        return self.service.validate_latest_knowledge(
            document_id,
        )

    def has_orphaned_knowledge(
        self,
        document_id: str,
    ) -> bool:
        return self.service.has_orphaned_knowledge(
            document_id,
        )

    def list_orphaned_knowledge(
        self,
        document_id: str,
    ):
        return self.service.list_orphaned_knowledge(
            document_id,
        )

    def remove_orphaned_knowledge(
        self,
        document_id: str,
    ) -> int:
        return self.service.remove_orphaned_knowledge(
            document_id
        )

    def remove_knowledge_for_version(
        self,
        document_id: str,
        version: int,
    ) -> int:
        return self.service.remove_knowledge_for_version(
            document_id=document_id,
            version=version,
        )

    def refresh_version_knowledge(
        self,
        *,
        document_id: str,
        from_version: int,
        to_version: int,
    ):
        return self.service.refresh_version_knowledge(
            document_id=document_id,
            from_version=from_version,
            to_version=to_version,
        )

    def list_documents_for_user(
        self,
        user_id: str,
    ) -> list[Document]:
        return self.service.list_documents_for_user(
            user_id
        )

    def list_documents_for_organization(
        self,
        organization_id: str,
    ) -> list[Document]:
        return self.service.list_documents_for_organization(
            organization_id
        )

    def list_documents_for_project(
        self,
        project_id: str,
    ) -> list[Document]:
        return self.service.list_documents_for_project(
            project_id
        )

    def list_documents_for_context(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> list[Document]:
        return self.service.list_documents_for_context(
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )
