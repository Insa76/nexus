from pathlib import Path

from documents import (
    DocumentArtifact,
    build_document_services,
)


def test_document_service_uses_format_ingestion_service(
    tmp_path: Path,
):
    services = build_document_services()

    document_path = tmp_path / "manual.txt"
    document_path.write_text(
        "NEXUS document content",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=str(document_path),
    )

    services.access.add_artifact(
        artifact
    )

    document = services.access.create_document(
        name="manual.txt",
        mime_type="text/plain",
        source=str(document_path),
        artifact_id=artifact.id,
    )

    resolution = services.access.ingest(
        document
    )

    assert resolution is not None
    assert resolution.document.content_id is not None
    assert resolution.content is not None
    assert resolution.content.text == (
        "NEXUS document content"
    )
    assert resolution.content.content_type == (
        "text/plain"
    )


def test_document_service_updates_document_timestamp(
    tmp_path: Path,
):
    services = build_document_services()

    document_path = tmp_path / "manual.txt"
    document_path.write_text(
        "timestamp test",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=str(document_path),
    )

    services.access.add_artifact(
        artifact
    )

    document = services.access.create_document(
        name="manual.txt",
        mime_type="text/plain",
        source=str(document_path),
        artifact_id=artifact.id,
    )

    original_updated_at = document.updated_at

    resolution = services.access.ingest(
        document
    )

    assert resolution is not None
    assert (
        resolution.document.updated_at
        >= original_updated_at
    )
