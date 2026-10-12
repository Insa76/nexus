"""NEXUS Assistant Documents."""

from .artifact_store import ArtifactStore
from .artifacts import DocumentArtifact
from .content import DocumentContent
from .content_store import ContentStore
from .ingestion import DocumentIngestor, IngestionResult
from .ingestion_registry import IngestionRegistry
from .metadata import DocumentMetadata
from .models import Document
from .resolver import DocumentResolution, DocumentResolver
from .store import DocumentStore
from .artifact_reader import ArtifactReader
from .text_ingestion import TextIngestor
from .local_artifact_reader import LocalArtifactReader
from .ingestion_service import DocumentIngestionService
from .service import DocumentService
from .services import DocumentServices, build_document_services
from .access import DocumentsAccess
from .document_type import DocumentType
from .type_resolver import DocumentTypeResolver
from .sources import DocumentSource
from .format_reader import DocumentFormatReader
from .text_format_reader import TextFormatReader
from .format_reader_registry import FormatReaderRegistry
from .format_ingestion import FormatIngestionService
from .artifact_type_resolver import ArtifactTypeResolver
from .extension_type_detection import ExtensionTypeDetectionStrategy
from .type_detection import DocumentTypeDetectionStrategy
from .declared_type_detection import (
    DeclaredTypeDetectionStrategy,
)
from .type_validation import DocumentTypeValidation
from .type_validator import DocumentTypeValidator
from .format_ingestion import (
    FormatIngestionResult,
)
from .document_ingestion_result import DocumentIngestionResult
from .type_detection_evidence import (
    DocumentTypeDetectionEvidence,
)
from .ingestion_evidence import DocumentIngestionEvidence
from .ingestion_record import DocumentIngestionRecord
from .ingestion_record_store import DocumentIngestionRecordStore
from .content_version import DocumentContentVersion
from .content_version_store import DocumentContentVersionStore
from .version_resolver import (
    DocumentVersionResolution,
    DocumentVersionResolver,
)
from .version_comparison import (
    DocumentVersionComparison,
    DocumentVersionComparator,
)
from .change import DocumentChange, DocumentChangeType
from .change_detector import (
    DocumentChangeDetection,
    DocumentChangeDetector,
)
from .version_change import DocumentVersionChangeResult
from .semantic_change import DocumentSemanticChange
from .semantic_analyzer import DocumentSemanticAnalyzer
from .rule_based_semantic_analyzer import RuleBasedSemanticAnalyzer
from .semantic_analysis import DocumentSemanticAnalysis
from .semantic_analysis_service import DocumentSemanticAnalysisService
from .knowledge import DocumentKnowledge
from .knowledge_extractor import DocumentKnowledgeExtractor
from .rule_based_knowledge_extractor import (
    RuleBasedDocumentKnowledgeExtractor,
)
from .knowledge_extraction import DocumentKnowledgeExtraction
from .knowledge_extraction_service import (
    DocumentKnowledgeExtractionService,
)
from .knowledge_record import DocumentKnowledgeRecord
from .knowledge_record_store import DocumentKnowledgeRecordStore
from .context_access import DocumentContextAccess
from .context_resolver import (
    DocumentContext,
    DocumentContextResolver,
    DocumentContextSelection,
)
from .context_relevance import (
    DocumentContextMatch,
    DocumentContextRelevance,
)
from .context_relevance_resolver import (
    DocumentContextRelevanceResolver,
)
from .query import DocumentQueryResult
from .capability import DocumentCapability
from .cognitive import DocumentCognitiveAccess, DocumentCognitiveResult


__all__ = [
    "ArtifactStore",
    "ContentStore",
    "Document",
    "DocumentArtifact",
    "DocumentContent",
    "DocumentIngestor",
    "DocumentMetadata",
    "DocumentResolution",
    "DocumentResolver",
    "DocumentStore",
    "IngestionRegistry",
    "IngestionResult",
    "ArtifactReader",
    "TextIngestor",
    "LocalArtifactReader",
    "DocumentIngestionService",
    "DocumentServices",
    "build_document_services",
    "DocumentsAccess",
    "DocumentType",
    "DocumentTypeResolver",
    "DocumentSource",
    "DocumentFormatReader",
    "TextFormatReader",
    "FormatReaderRegistry",
    "FormatIngestionService",
    "ArtifactTypeResolver",
    "ExtensionTypeDetectionStrategy",
    "DocumentTypeDetectionStrategy",
    "DeclaredTypeDetectionStrategy",
    "DocumentTypeValidation",
    "DocumentTypeValidator",
    "FormatIngestionResult",
    "DocumentIngestionResult",
    "DocumentTypeDetectionEvidence",
    "DocumentIngestionEvidence",
    "DocumentIngestionRecord",
    "DocumentIngestionRecordStore",
    "DocumentContentVersion",
    "DocumentContentVersionStore",
    "DocumentVersionChangeResult",
    "DocumentVersionResolution",
    "DocumentVersionResolver",
    "DocumentVersionComparison",
    "DocumentVersionComparator",
    "DocumentChange",
    "DocumentChangeDetection",
    "DocumentChangeDetector",
    "DocumentSemanticChange",
    "DocumentSemanticAnalyzer",
    "RuleBasedSemanticAnalyzer",
    "DocumentSemanticAnalysis",
    "DocumentSemanticAnalysisService",
    "DocumentKnowledge",
    "DocumentKnowledgeExtractor",
    "RuleBasedDocumentKnowledgeExtractor",
    "DocumentKnowledgeExtraction",
    "DocumentKnowledgeExtractionService",
    "DocumentKnowledgeRecord",
    "DocumentKnowledgeRecordStore",
    "DocumentContext",
    "DocumentContextAccess",
    "DocumentContextResolver",
    "DocumentContextSelection",
    "DocumentContextMatch",
    "DocumentContextRelevance",
    "DocumentContextRelevanceResolver",
    "DocumentQueryResult",
    "DocumentQueryResult",
    "DocumentCapability",
    "DocumentCognitiveAccess",
    "DocumentCognitiveResult",

]
