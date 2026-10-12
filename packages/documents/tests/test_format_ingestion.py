from documents import (
    DocumentArtifact,
    DocumentType,
    FormatIngestionService,
    FormatReaderRegistry,
)


class FakeFormatReader:
    def __init__(self, text: str = "document content") -> None:
        self.text = text

    def supports(self, document_type):
        return True

    def read(self, artifact, document_type):
        return self.text


def test_format_ingestion_reads_registered_format():
    registry = FormatReaderRegistry()

    reader = FakeFormatReader(
        text="hello nexus"
    )

    registry.register(
        "text/plain",
        reader,
    )

    service = FormatIngestionService(
        reader_registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:C:/documents/test.txt",
    )

    result = service.ingest(
        artifact=artifact,
        document_type="text/plain",
    )

    assert result.artifact is artifact
    assert result.content.text == "hello nexus"
    assert result.content.content_type == "text/plain"


def test_format_ingestion_accepts_document_type():
    registry = FormatReaderRegistry()

    reader = FakeFormatReader(
        text="typed content"
    )

    registry.register(
        "text/plain",
        reader,
    )

    service = FormatIngestionService(
        reader_registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:C:/documents/test.txt",
    )

    document_type = DocumentType.from_mime_type(
        "TEXT/PLAIN"
    )

    result = service.ingest(
        artifact=artifact,
        document_type=document_type,
    )

    assert result.content.text == "typed content"
    assert result.content.content_type == "text/plain"


def test_format_ingestion_normalizes_content_type():
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
        location="local:C:/documents/test.txt",
    )

    result = service.ingest(
        artifact=artifact,
        document_type=" TEXT/PLAIN ",
    )

    assert result.content.content_type == "text/plain"


def test_format_ingestion_rejects_unsupported_format():
    registry = FormatReaderRegistry()

    service = FormatIngestionService(
        reader_registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:C:/documents/test.pdf",
    )

    try:
        service.ingest(
            artifact=artifact,
            document_type="application/pdf",
        )
    except ValueError as exc:
        assert (
            "No format reader registered"
            in str(exc)
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_format_ingestion_lists_supported_formats():
    registry = FormatReaderRegistry()

    registry.register(
        "text/plain",
        FakeFormatReader(),
    )

    registry.register(
        "application/pdf",
        FakeFormatReader(),
    )

    service = FormatIngestionService(
        reader_registry=registry,
    )

    assert service.supported_content_types() == [
        "text/plain",
        "application/pdf",
    ]
