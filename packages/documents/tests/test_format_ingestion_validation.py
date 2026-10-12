from documents import (
    ArtifactTypeResolver,
    DocumentArtifact,
    FormatIngestionResult,
    FormatIngestionService,
    FormatReaderRegistry,
    DocumentType,
)


class FakeFormatReader:
    def read(self, artifact, document_type):
        return "validated content"


def build_service():
    registry = FormatReaderRegistry()

    registry.register(
        "text/plain",
        FakeFormatReader(),
    )

    return FormatIngestionService(
        reader_registry=registry,
        type_resolver=ArtifactTypeResolver(),
    )


def test_ingestion_validation_reports_match():
    service = build_service()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = service.ingest_with_validation(
        artifact=artifact,
        declared_type="text/plain",
    )

    assert isinstance(
        result,
        FormatIngestionResult,
    )
    assert result.type_validation is not None
    assert result.type_validation.matches
    assert (
        result.ingestion.content.text
        == "validated content"
    )


def test_ingestion_validation_reports_mismatch():
    service = build_service()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = service.ingest_with_validation(
        artifact=artifact,
        declared_type="application/pdf",
    )

    assert result.type_validation is not None
    assert result.type_validation.mismatch
    assert (
        result.type_validation.declared_type.mime_type
        == "application/pdf"
    )
    assert (
        result.type_validation.detected_type.mime_type
        == "text/plain"
    )


def test_ingestion_still_completes_on_type_mismatch():
    service = build_service()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = service.ingest_with_validation(
        artifact=artifact,
        declared_type="application/pdf",
    )

    assert result.ingestion.content.text == (
        "validated content"
    )
