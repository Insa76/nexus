from __future__ import annotations

from dataclasses import dataclass

from documents.access import DocumentsAccess
from documents.artifact_reader import ArtifactReader
from documents.artifact_store import ArtifactStore
from documents.artifact_type_resolver import ArtifactTypeResolver
from documents.content_store import ContentStore
from documents.content_version_store import DocumentContentVersionStore
from documents.format_ingestion import FormatIngestionService
from documents.format_reader_registry import FormatReaderRegistry
from documents.ingestion_record_store import DocumentIngestionRecordStore
from documents.ingestion_registry import IngestionRegistry
from documents.ingestion_service import DocumentIngestionService
from documents.local_artifact_reader import LocalArtifactReader
from documents.service import DocumentService
from documents.store import DocumentStore
from documents.text_format_reader import TextFormatReader
from documents.text_ingestion import TextIngestor
from documents.type_resolver import DocumentTypeResolver
from documents.rule_based_semantic_analyzer import RuleBasedSemanticAnalyzer
from documents.semantic_analysis_service import DocumentSemanticAnalysisService
from documents.rule_based_knowledge_extractor import (
    RuleBasedDocumentKnowledgeExtractor,
)
from documents.knowledge_extraction_service import (
    DocumentKnowledgeExtractionService,
)
from documents.knowledge_record_store import DocumentKnowledgeRecordStore
from documents.context_access import DocumentContextAccess
from documents.context_resolver import DocumentContextResolver


@dataclass(slots=True)
class DocumentServices:
    document_store: DocumentStore
    artifact_store: ArtifactStore
    content_store: ContentStore

    ingestion_registry: IngestionRegistry
    type_resolver: DocumentTypeResolver
    ingestion_service: DocumentIngestionService

    artifact_type_resolver: ArtifactTypeResolver
    format_reader_registry: FormatReaderRegistry
    format_ingestion_service: FormatIngestionService
    ingestion_record_store: DocumentIngestionRecordStore
    content_version_store: DocumentContentVersionStore
    semantic_analysis_service: DocumentSemanticAnalysisService
    knowledge_extraction_service: DocumentKnowledgeExtractionService
    knowledge_record_store: DocumentKnowledgeRecordStore

    document_service: DocumentService
    access: DocumentsAccess
    context_access: DocumentContextAccess


def build_document_services() -> DocumentServices:
    document_store = DocumentStore()
    artifact_store = ArtifactStore()
    content_store = ContentStore()

    ingestion_registry = IngestionRegistry()
    type_resolver = DocumentTypeResolver()
    artifact_type_resolver = ArtifactTypeResolver()

    artifact_reader: ArtifactReader = LocalArtifactReader()

    ingestion_record_store = DocumentIngestionRecordStore()
    content_version_store = DocumentContentVersionStore()
    knowledge_record_store = DocumentKnowledgeRecordStore()

    semantic_analysis_service = DocumentSemanticAnalysisService(
        analyzer=RuleBasedSemanticAnalyzer(),
    )

    knowledge_extraction_service = DocumentKnowledgeExtractionService(
    extractor=RuleBasedDocumentKnowledgeExtractor(),
    )

    text_ingestor = TextIngestor(
        reader=artifact_reader,
    )

    ingestion_registry.register(
        "text/plain",
        text_ingestor,
    )

    ingestion_service = DocumentIngestionService(
        registry=ingestion_registry,
        type_resolver=type_resolver,
    )

    format_reader_registry = FormatReaderRegistry()

    text_format_reader = TextFormatReader(
        artifact_reader=artifact_reader,
    )

    format_reader_registry.register(
        "text/plain",
        text_format_reader,
    )

    format_ingestion_service = FormatIngestionService(
        reader_registry=format_reader_registry,
        type_resolver=artifact_type_resolver,
    )

    document_service = DocumentService(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
        ingestion_service=ingestion_service,
        format_ingestion_service=format_ingestion_service,
        ingestion_record_store=ingestion_record_store,
        content_version_store=content_version_store,
        semantic_analysis_service=semantic_analysis_service,
        knowledge_extraction_service=knowledge_extraction_service,
        knowledge_record_store=knowledge_record_store,
    )

    access = DocumentsAccess(
        service=document_service,
    )
    context_resolver = DocumentContextResolver(
        access,
    )

    context_access = DocumentContextAccess(
        context_resolver,
    )

    return DocumentServices(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
        ingestion_registry=ingestion_registry,
        type_resolver=type_resolver,
        ingestion_service=ingestion_service,
        artifact_type_resolver=artifact_type_resolver,
        format_reader_registry=format_reader_registry,
        format_ingestion_service=format_ingestion_service,
        ingestion_record_store=ingestion_record_store,
        content_version_store=content_version_store,
        semantic_analysis_service=semantic_analysis_service,
        knowledge_extraction_service=knowledge_extraction_service,
        knowledge_record_store=knowledge_record_store,
        document_service=document_service,
        access=access,
        context_access=context_access,
    )
