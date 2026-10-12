from pathlib import Path

from documents import (
    DocumentArtifact,
    IngestionRegistry,
    LocalArtifactReader,
    TextIngestor,
)


def test_local_text_ingestion_flow(tmp_path: Path):
    file_path = tmp_path / "contract.txt"
    file_path.write_text(
        "Este es el contenido del contrato.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    reader = LocalArtifactReader()
    ingestor = TextIngestor(reader)

    registry = IngestionRegistry()
    registry.register("text/plain", ingestor)

    selected_ingestor = registry.get("text/plain")

    assert selected_ingestor is ingestor

    result = selected_ingestor.ingest(artifact)

    assert result.artifact is artifact
    assert result.content.text == "Este es el contenido del contrato."
    assert result.content.content_type == "text/plain"


def test_registry_selects_text_ingestor_for_local_artifact(tmp_path: Path):
    file_path = tmp_path / "notes.txt"
    file_path.write_text(
        "Notas de NEXUS.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    registry = IngestionRegistry()

    registry.register(
        "text/plain",
        TextIngestor(LocalArtifactReader()),
    )

    ingestor = registry.get("text/plain")

    assert ingestor is not None

    result = ingestor.ingest(artifact)

    assert result.artifact is artifact
    assert result.content.text == "Notas de NEXUS."


def test_unsupported_content_type_is_not_selected(tmp_path: Path):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "Contenido.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=f"local:{file_path}",
    )

    registry = IngestionRegistry()
    registry.register(
        "text/plain",
        TextIngestor(LocalArtifactReader()),
    )

    assert registry.get("application/pdf") is None
    assert not registry.supports("application/pdf")
