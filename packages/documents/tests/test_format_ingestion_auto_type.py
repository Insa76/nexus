from documents import (
    ArtifactTypeResolver,
    DocumentArtifact,
    FormatIngestionService,
    FormatReaderRegistry,
)


class FakeFormatReader:
    def read(self, artifact, document_type):
        return "auto detected content"


def test_format_ingestion_resolves_type_from_artifact():
    registry = FormatReaderRegistry()

    registry.register(
        "text/plain",
        FakeFormatReader(),
    )

    service = FormatIngestionService(
        reader_registry=registry,
        type_resolver=ArtifactTypeResolver(),
    )

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = service.ingest(
        artifact=artifact,
    )

    assert result.content.text == "auto detected content"
    assert result.content.content_type == "text/plain"


def test_explicit_type_overrides_artifact_detection():
    registry = FormatReaderRegistry()

    reader = FakeFormatReader()

    registry.register(
        "text/plain",
        reader,
    )

    service = FormatIngestionService(
        reader_registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    result = service.ingest(
        artifact=artifact,
        document_type="text/plain",
    )

    assert result.content.content_type == "text/plain"


def test_composed_services_share_artifact_type_resolver():
    from documents import build_document_services

    services = build_document_services()

    assert (
        services.format_ingestion_service._type_resolver
        is services.artifact_type_resolver
    )
