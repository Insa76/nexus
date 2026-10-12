import pytest

from documents import (
    DocumentArtifact,
    DocumentIngestionService,
    DocumentType,
    IngestionRegistry,
)


class FakeIngestor:
    def __init__(self):
        self.artifacts = []

    def ingest(self, artifact):
        self.artifacts.append(artifact)
        return artifact


def test_ingestion_service_normalizes_mime_type():
    registry = IngestionRegistry()
    ingestor = FakeIngestor()

    registry.register(
        "text/plain",
        ingestor,
    )

    service = DocumentIngestionService(
        registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:test.txt",
    )

    result = service.ingest(
        artifact,
        " TEXT/PLAIN ",
    )

    assert result == artifact
    assert ingestor.artifacts == [artifact]


def test_ingestion_service_accepts_document_type():
    registry = IngestionRegistry()
    ingestor = FakeIngestor()

    registry.register(
        "application/pdf",
        ingestor,
    )

    service = DocumentIngestionService(
        registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:test.pdf",
    )

    document_type = DocumentType.from_mime_type(
        "APPLICATION/PDF"
    )

    result = service.ingest(
        artifact,
        document_type,
    )

    assert result == artifact
    assert ingestor.artifacts == [artifact]


def test_ingestion_service_uses_normalized_type_for_lookup():
    registry = IngestionRegistry()
    ingestor = FakeIngestor()

    registry.register(
        "text/plain",
        ingestor,
    )

    service = DocumentIngestionService(
        registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:test.txt",
    )

    service.ingest(
        artifact,
        "Text/Plain",
    )

    assert len(ingestor.artifacts) == 1


def test_ingestion_service_rejects_invalid_mime_type():
    registry = IngestionRegistry()

    service = DocumentIngestionService(
        registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:test.txt",
    )

    with pytest.raises(ValueError):
        service.ingest(
            artifact,
            "invalid",
        )


def test_ingestion_service_reports_normalized_missing_type():
    registry = IngestionRegistry()

    service = DocumentIngestionService(
        registry=registry,
    )

    artifact = DocumentArtifact.create(
        location="local:test.pdf",
    )

    with pytest.raises(
        ValueError,
        match="application/pdf",
    ):
        service.ingest(
            artifact,
            "APPLICATION/PDF",
        )

def test_ingestion_service_reports_supported_content_types():
    registry = IngestionRegistry()

    registry.register(
        "text/plain",
        FakeIngestor(),
    )

    registry.register(
        "application/pdf",
        FakeIngestor(),
    )

    service = DocumentIngestionService(
        registry=registry,
    )

    assert service.supported_content_types() == [
        "text/plain",
        "application/pdf",
    ]
