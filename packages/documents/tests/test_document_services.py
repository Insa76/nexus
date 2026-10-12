from documents import (
    FormatIngestionService,
    FormatReaderRegistry,
    TextFormatReader,
    DocumentIngestionRecordStore,
    DocumentContentVersionStore,
    DocumentArtifact,
    build_document_services,
)

from documents.context_access import DocumentContextAccess

def test_document_services_build_format_reader_registry():
    services = build_document_services()

    assert isinstance(
        services.format_reader_registry,
        FormatReaderRegistry,
    )


def test_document_services_registers_text_format_reader():
    services = build_document_services()

    reader = services.format_reader_registry.get(
        "text/plain"
    )

    assert isinstance(
        reader,
        TextFormatReader,
    )


def test_document_services_build_format_ingestion_service():
    services = build_document_services()

    assert isinstance(
        services.format_ingestion_service,
        FormatIngestionService,
    )


def test_document_services_supports_text_plain_format():
    services = build_document_services()

    assert services.format_reader_registry.supports(
        "text/plain"
    )


def test_document_services_exposes_text_format():
    services = build_document_services()

    assert services.format_ingestion_service.supported_content_types() == [
        "text/plain",
    ]

def test_document_services_build_ingestion_record_store():
    services = build_document_services()

    assert isinstance(
        services.ingestion_record_store,
        DocumentIngestionRecordStore,
    )

    assert (
        services.document_service.ingestion_record_store
        is services.ingestion_record_store
    )

def test_document_services_can_ingest_and_create_content_version(
    tmp_path,
):
    source = tmp_path / "versioned.txt"

    source.write_text(
        "Primera versión.",
        encoding="utf-8",
    )

    services = build_document_services()

    artifact = DocumentArtifact.create(
        location=f"local:{source}",
    )

    services.document_service.add_artifact(
        artifact
    )

    document = services.document_service.create_document(
        name="versioned.txt",
        mime_type="text/plain",
        source=f"local:{source}",
        artifact_id=artifact.id,
    )

    first_result = services.document_service.ingest(
        document
    )

    versions = (
        services.content_version_store
        .list_for_document(document.id)
    )

    assert first_result.content is not None
    assert len(versions) == 1

    assert versions[0].version == 1
    assert versions[0].document_id == document.id
    assert versions[0].content_id == (
        first_result.content.id
    )

def test_document_services_expose_document_context_access():
    services = build_document_services()

    assert isinstance(
        services.context_access,
        DocumentContextAccess,
    )


def test_document_context_access_uses_shared_document_access():
    services = build_document_services()

    document = services.access.create_document(
        name="Documento",
        mime_type="text/plain",
        source="document.txt",
        user_id="user-a",
    )

    result = services.context_access.resolve(
        user_id="user-a",
    )

    assert result.documents == (document,)
