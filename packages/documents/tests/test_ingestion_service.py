import pytest

from documents import (
    DocumentArtifact,
    DocumentIngestionService,
    IngestionRegistry,
    LocalArtifactReader,
    TextIngestor,
)


def build_service() -> DocumentIngestionService:
    registry = IngestionRegistry()

    registry.register(
        "text/plain",
        TextIngestor(LocalArtifactReader()),
    )

    return DocumentIngestionService(registry)


def test_service_ingests_registered_content_type(tmp_path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Contenido del documento.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    service = build_service()

    result = service.ingest(
        artifact=artifact,
        content_type="text/plain",
    )

    assert result.artifact is artifact
    assert result.content.text == "Contenido del documento."
    assert result.content.content_type == "text/plain"


def test_service_rejects_unsupported_content_type(tmp_path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Contenido.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    service = build_service()

    with pytest.raises(
        ValueError,
        match="No ingestor registered for content type: application/pdf",
    ):
        service.ingest(
            artifact=artifact,
            content_type="application/pdf",
        )


def test_service_uses_registry_selected_ingestor(tmp_path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text(
        "Notas de NEXUS.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    service = build_service()

    result = service.ingest(
        artifact=artifact,
        content_type="text/plain",
    )

    assert result.artifact.id == artifact.id
    assert result.content.text == "Notas de NEXUS."
