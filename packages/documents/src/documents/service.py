from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from documents.artifact_store import ArtifactStore
from documents.artifacts import DocumentArtifact
from documents.content_store import ContentStore
from documents.document_ingestion_result import DocumentIngestionResult
from documents.format_ingestion import FormatIngestionService
from documents.ingestion_evidence import DocumentIngestionEvidence
from documents.ingestion_record import DocumentIngestionRecord
from documents.ingestion_record_store import DocumentIngestionRecordStore
from documents.ingestion_service import DocumentIngestionService
from documents.models import Document
from documents.resolver import DocumentResolution, DocumentResolver
from documents.store import DocumentStore
from documents.type_validation import DocumentTypeValidation
from documents.content_version import DocumentContentVersion
from documents.content_version_store import DocumentContentVersionStore
from documents.change_detector import DocumentChangeDetector
from documents.version_change import DocumentVersionChangeResult
from documents.version_comparison import DocumentVersionComparator
from documents.version_resolver import DocumentVersionResolver
from documents.semantic_analysis import DocumentSemanticAnalysis
from documents.semantic_analysis_service import DocumentSemanticAnalysisService
from documents.knowledge_extraction import DocumentKnowledgeExtraction
from documents.knowledge_extraction_service import (
    DocumentKnowledgeExtractionService,
)
from documents.knowledge_record import DocumentKnowledgeRecord
from documents.knowledge_record_store import DocumentKnowledgeRecordStore
from documents.content import DocumentContent


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class DocumentService:
    document_store: DocumentStore
    artifact_store: ArtifactStore
    content_store: ContentStore
    ingestion_service: DocumentIngestionService
    format_ingestion_service: FormatIngestionService | None = None
    ingestion_record_store: DocumentIngestionRecordStore | None = None
    content_version_store: DocumentContentVersionStore | None = None
    semantic_analysis_service: DocumentSemanticAnalysisService | None = None
    knowledge_extraction_service: DocumentKnowledgeExtractionService | None = None
    knowledge_record_store: DocumentKnowledgeRecordStore | None = None

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
        document = Document.create(
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

        return self.document_store.add(document)

    def get_document(
        self,
        document_id: str,
    ) -> Document | None:
        return self.document_store.get(
            document_id,
        )

    def get_artifact(
        self,
        artifact_id: str,
    ) -> DocumentArtifact | None:
        return self.artifact_store.get(
            artifact_id,
        )

    def get_content(
        self,
        content_id: str,
    ) -> DocumentContent | None:
        return self.content_store.get(
            content_id,
        )

    def update_document(
        self,
        document: Document,
    ) -> Document:
        return self.document_store.update(
            document,
        )

    def count_documents(self) -> int:
        return self.document_store.count()

    def list_documents(self) -> list[Document]:
        return self.document_store.list()

    def list_documents_for_user(
        self,
        user_id: str,
    ) -> list[Document]:
        return self.document_store.list_for_user(
            user_id
        )

    def list_documents_for_organization(
        self,
        organization_id: str,
    ) -> list[Document]:
        return self.document_store.list_for_organization(
            organization_id
        )

    def list_documents_for_project(
        self,
        project_id: str,
    ) -> list[Document]:
        return self.document_store.list_for_project(
            project_id
        )

    def list_documents_for_context(
        self,
        *,
        user_id: str | None = None,
        organization_id: str | None = None,
        project_id: str | None = None,
    ) -> list[Document]:
        return self.document_store.list_for_context(
            user_id=user_id,
            organization_id=organization_id,
            project_id=project_id,
        )

    def remove_document(
        self,
        document_id: str,
    ) -> Document | None:
        document = self.document_store.get(
            document_id
        )

        if document is None:
            return None

        if self.knowledge_record_store is not None:
            self.knowledge_record_store.remove_for_document(
                document_id
            )

        if self.ingestion_record_store is not None:
            self.ingestion_record_store.remove_for_document(
                document_id
            )

        if self.content_version_store is not None:
            self.content_version_store.remove_for_document(
                document_id
            )

        return self.document_store.remove(
            document_id
        )

    def add_artifact(
        self,
        artifact: DocumentArtifact,
    ) -> DocumentArtifact:
        return self.artifact_store.add(artifact)

    def ingest(
        self,
        document: Document,
    ) -> DocumentResolution:
        result = self.ingest_with_validation(document)

        return result.resolution

    def ingest_with_validation(
        self,
        document: Document,
    ) -> DocumentIngestionResult:
        if document.artifact_id is None:
            raise ValueError(
                f"Document has no artifact: {document.id}"
            )

        artifact = self.artifact_store.get(
            document.artifact_id
        )

        if artifact is None:
            raise ValueError(
                f"Artifact not found: {document.artifact_id}"
            )

        type_validation: DocumentTypeValidation | None = None
        detection_evidence = None
        ingestion_evidence = None

        if self.format_ingestion_service is None:
            result = self.ingestion_service.ingest(
                artifact=artifact,
                content_type=document.mime_type,
            )
        else:
            format_result = (
                self.format_ingestion_service.ingest_with_validation(
                    artifact=artifact,
                    declared_type=document.mime_type,
                )
            )

            result = format_result.ingestion

            type_validation = format_result.type_validation
            detection_evidence = format_result.detection_evidence

            if (
                type_validation is not None
                and detection_evidence is not None
            ):
                ingestion_evidence = DocumentIngestionEvidence(
                    declared_type=type_validation.declared_type,
                    detected_type=detection_evidence.detected_type,
                    detection_strategy=detection_evidence.strategy,
                )

        self.content_store.add(result.content)

        if self.content_version_store is not None:
            version_number = (
                self.content_version_store.get_next_version(
                    document.id
                )
            )

            content_version = DocumentContentVersion.create(
                document_id=document.id,
                content_id=result.content.id,
                version=version_number,
                content_type=result.content.content_type,
            )

            self.content_version_store.add(
                content_version
            )

        updated_document = Document(
            id=document.id,
            name=document.name,
            mime_type=document.mime_type,
            source=document.source,
            description=document.description,
            user_id=document.user_id,
            organization_id=document.organization_id,
            project_id=document.project_id,
            artifact_id=document.artifact_id,
            content_id=result.content.id,
            metadata=dict(document.metadata),
            ingestion_evidence=(
                ingestion_evidence
                if ingestion_evidence is not None
                else document.ingestion_evidence
            ),
            created_at=document.created_at,
            updated_at=_utc_now(),
        )

        self.document_store.update(
            updated_document
        )

        if self.ingestion_record_store is not None:
            record = DocumentIngestionRecord.create(
                document_id=updated_document.id,
                artifact_id=artifact.id,
                content_id=result.content.id,
                declared_type=document.mime_type,
                detected_type=(
                    detection_evidence.detected_type
                    if detection_evidence is not None
                    else None
                ),
                detection_strategy=(
                    detection_evidence.strategy
                    if detection_evidence is not None
                    else None
                ),
                type_matches=(
                    type_validation.matches
                    if type_validation is not None
                    else None
                ),
            )

            self.ingestion_record_store.add(record)

        resolution = self.resolve(
            updated_document.id
        )

        return DocumentIngestionResult(
            resolution=resolution,
            type_validation=type_validation,
            detection_evidence=detection_evidence,
        )

    def list_ingestion_history(
        self,
        document_id: str,
    ) -> list[DocumentIngestionRecord]:
        if self.ingestion_record_store is None:
            return []

        return self.ingestion_record_store.list_for_document(
            document_id
        )
    def list_knowledge_history(
        self,
        document_id: str,
    ) -> list[DocumentKnowledgeRecord]:
        if self.knowledge_record_store is None:
            return []

        return self.knowledge_record_store.list_for_document(
            document_id
        )

    def list_latest_knowledge(
        self,
        document_id: str,
    ) -> list[DocumentKnowledgeRecord]:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return []

        latest_version = (
            self.content_version_store.get_latest_for_document(
                document_id
            )
        )

        if latest_version is None:
            return []

        return self.knowledge_record_store.list_for_content_version(
            latest_version.id
        )

    def list_knowledge_for_version(
        self,
        document_id: str,
        version: int,
    ) -> list[DocumentKnowledgeRecord]:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return []

        content_version = (
            DocumentVersionResolver(
                store=self.content_version_store,
            ).resolve_version(
                document_id=document_id,
                version=version,
            )
        )

        return self.knowledge_record_store.list_for_content_version(
            content_version.id
        )

    def list_versions(
        self,
        document_id: str,
    ) -> list[DocumentContentVersion]:
        return self.content_version_store.list_for_document(
            document_id,
        )

    def get_version(
        self,
        version_id: str,
    ) -> DocumentContentVersion | None:
        return self.content_version_store.get(
            version_id,
        )

    def get_latest_version(
        self,
        document_id: str,
    ) -> DocumentContentVersion | None:
        return self.content_version_store.get_latest_for_document(
            document_id,
        )

    def has_latest_knowledge(
        self,
        document_id: str,
    ) -> bool:
        return bool(
            self.list_latest_knowledge(
                document_id,
            )
        )

    def knowledge_count(
        self,
        document_id: str,
    ) -> int:
        return len(
            self.list_latest_knowledge(
                document_id,
            )
        )

    def validate_latest_knowledge(
        self,
        document_id: str,
    ) -> bool:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return False

        latest_version = (
            self.content_version_store.get_latest_for_document(
            document_id
            )
        )

        if latest_version is None:
            return False

        records = (
            self.knowledge_record_store.list_for_document(
                document_id
            )
        )

        return all(
            record.content_version_id
            == latest_version.id
            for record in records
        )

    def has_orphaned_knowledge(
        self,
            document_id: str,
    ) -> bool:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return False

        records = self.knowledge_record_store.list_for_document(
            document_id
        )

        for record in records:
            try:
                self.content_version_store.get(
                    record.content_version_id
                )
            except AttributeError:
                return False

            if (
                self.content_version_store.get(
                    record.content_version_id
                )
                is None
            ):
                return True

        return False

    def list_orphaned_knowledge(
        self,
        document_id: str,
    ) -> list[DocumentKnowledgeRecord]:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return []

        records = self.knowledge_record_store.list_for_document(
            document_id
        )

        orphaned: list[DocumentKnowledgeRecord] = []

        for record in records:
            content_version = self.content_version_store.get(
                record.content_version_id
            )

            if content_version is None:
                orphaned.append(record)

        return orphaned

    def remove_knowledge_for_version(
        self,
        document_id: str,
        version: int,
    ) -> int:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return 0

        content_version_id = self._resolve_content_version_id(
            document_id=document_id,
            version=version,
        )

        return self.knowledge_record_store.remove_for_content_version(
            content_version_id
        )

    def remove_orphaned_knowledge(
        self,
        document_id: str,
    ) -> int:
        if (
            self.knowledge_record_store is None
            or self.content_version_store is None
        ):
            return 0

        orphaned = self.list_orphaned_knowledge(
            document_id
        )

        removed = 0

        for record in orphaned:
            self.knowledge_record_store.remove(
                record.id
            )
            removed += 1

        return removed

    def _resolve_content_version_id(
        self,
        *,
        document_id: str,
        version: int,
    ) -> str:
        if self.content_version_store is None:
            raise ValueError(
                "Document content version store is not configured"
            )

        resolver = DocumentVersionResolver(
            store=self.content_version_store,
        )

        content_version = resolver.resolve_version(
            document_id=document_id,
            version=version,
        )

        return content_version.id

    def compare_versions(
        self,
        *,
        document_id: str,
        from_version: int,
        to_version: int,
    ) -> DocumentVersionChangeResult:
        if self.content_version_store is None:
            raise ValueError(
                "Document content version store is not configured"
            )

        resolver = DocumentVersionResolver(
            store=self.content_version_store,
        )

        resolution = resolver.resolve_pair(
            document_id=document_id,
            from_version=from_version,
            to_version=to_version,
        )

        from_content = self.content_store.get(
            resolution.from_version.content_id
        )

        if from_content is None:
            raise ValueError(
                "Document content not found: "
                f"{resolution.from_version.content_id}"
            )

        to_content = self.content_store.get(
            resolution.to_version.content_id
        )

        if to_content is None:
            raise ValueError(
                "Document content not found: "
                f"{resolution.to_version.content_id}"
            )

        comparator = DocumentVersionComparator()
        comparison = comparator.compare(resolution)

        detector = DocumentChangeDetector()
        detection = detector.detect(
            comparison=comparison,
            before_text=from_content.text,
            after_text=to_content.text,
        )

        return DocumentVersionChangeResult(
            comparison=comparison,
            changes=detection.changes,
        )

    def compare_latest_versions(
        self,
        *,
        document_id: str,
    ) -> DocumentVersionChangeResult:
        if self.content_version_store is None:
            raise ValueError(
                "Document content version store is not configured"
            )

        resolver = DocumentVersionResolver(
            store=self.content_version_store,
        )

        resolution = resolver.resolve_latest_pair(
            document_id=document_id,
        )

        from_content = self.content_store.get(
            resolution.from_version.content_id
        )

        if from_content is None:
            raise ValueError(
                "Document content not found: "
                f"{resolution.from_version.content_id}"
            )

        to_content = self.content_store.get(
            resolution.to_version.content_id
        )

        if to_content is None:
            raise ValueError(
                "Document content not found: "
                f"{resolution.to_version.content_id}"
            )

        comparator = DocumentVersionComparator()
        comparison = comparator.compare(resolution)

        detector = DocumentChangeDetector()
        detection = detector.detect(
            comparison=comparison,
            before_text=from_content.text,
            after_text=to_content.text,
        )

        return DocumentVersionChangeResult(
            comparison=comparison,
            changes=detection.changes,
        )

    def analyze_version_changes(
        self,
        *,
        document_id: str,
        from_version: int,
        to_version: int,
    ) -> DocumentSemanticAnalysis:
        if self.semantic_analysis_service is None:
            raise ValueError(
                "Document semantic analysis service is not configured"
            )

        result = self.compare_versions(
            document_id=document_id,
            from_version=from_version,
            to_version=to_version,
        )

        return self.semantic_analysis_service.analyze(result)

    def analyze_latest_version_changes(
        self,
        *,
        document_id: str,
    ) -> DocumentSemanticAnalysis:
        if self.semantic_analysis_service is None:
            raise ValueError(
                "Document semantic analysis service is not configured"
            )

        result = self.compare_latest_versions(
            document_id=document_id,
        )

        return self.semantic_analysis_service.analyze(result)

    def _store_knowledge_records(
        self,
        *,
        document_id: str,
        content_version_id: str,
        extraction: DocumentKnowledgeExtraction,
    ) -> None:
        if self.knowledge_record_store is None:
            return

        for knowledge in extraction.knowledge:
            existing = self.knowledge_record_store.find(
                document_id=document_id,
                content_version_id=content_version_id,
                knowledge=knowledge,
            )

            if existing is not None:
                continue

            record = DocumentKnowledgeRecord.create(
                document_id=document_id,
                content_version_id=content_version_id,
                knowledge=knowledge,
            )

            self.knowledge_record_store.add(record)

    def extract_version_knowledge(
        self,
        *,
        document_id: str,
        from_version: int,
        to_version: int,
    ) -> DocumentKnowledgeExtraction:
        if self.semantic_analysis_service is None:
            raise ValueError(
                "Document semantic analysis service is not configured"
            )

        if self.knowledge_extraction_service is None:
            raise ValueError(
                "Document knowledge extraction service is not configured"
            )

        analysis = self.analyze_version_changes(
            document_id=document_id,
            from_version=from_version,
            to_version=to_version,
        )

        extraction = self.knowledge_extraction_service.extract(
            analysis
        )

        content_version_id = self._resolve_content_version_id(
            document_id=document_id,
            version=to_version,
        )

        self._store_knowledge_records(
            document_id=document_id,
            content_version_id=content_version_id,
            extraction=extraction,
        )

        return extraction

    def refresh_version_knowledge(
        self,
        *,
        document_id: str,
        from_version: int,
        to_version: int,
    ) -> DocumentKnowledgeExtraction:
        if self.semantic_analysis_service is None:
            raise ValueError(
                "Document semantic analysis service is not configured"
            )

        if self.knowledge_extraction_service is None:
            raise ValueError(
                "Document knowledge extraction service is not configured"
            )

        analysis = self.analyze_version_changes(
            document_id=document_id,
            from_version=from_version,
            to_version=to_version,
        )

        extraction = self.knowledge_extraction_service.extract(
            analysis
        )

        content_version_id = self._resolve_content_version_id(
            document_id=document_id,
            version=to_version,
        )

        if self.knowledge_record_store is not None:
            self.knowledge_record_store.remove_for_content_version(
                content_version_id
            )

        self._store_knowledge_records(
            document_id=document_id,
            content_version_id=content_version_id,
            extraction=extraction,
        )

        return extraction

    def extract_latest_version_knowledge(
        self,
        *,
        document_id: str,
    ) -> DocumentKnowledgeExtraction:
        if self.semantic_analysis_service is None:
            raise ValueError(
                "Document semantic analysis service is not configured"
            )

        if self.knowledge_extraction_service is None:
            raise ValueError(
                "Document knowledge extraction service is not configured"
            )

        analysis = self.analyze_latest_version_changes(
            document_id=document_id,
        )

        extraction = self.knowledge_extraction_service.extract(
            analysis
        )

        content_version_id = self._resolve_content_version_id(
            document_id=document_id,
            version=analysis.source.comparison.to_version,
        )

        self._store_knowledge_records(
            document_id=document_id,
            content_version_id=content_version_id,
            extraction=extraction,
        )

        return extraction

    def list_documents_for_user(
        self,
        user_id: str,
    ) -> list[Document]:
        return self.document_store.list_for_user(user_id)

    def resolve(
        self,
        document_id: str,
    ) -> DocumentResolution | None:
        resolver = DocumentResolver(
            document_store=self.document_store,
            artifact_store=self.artifact_store,
            content_store=self.content_store,
        )

        return resolver.resolve(
            document_id
        )
