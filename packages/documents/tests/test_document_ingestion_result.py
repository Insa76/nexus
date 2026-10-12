from pathlib import Path

from documents import (
    DocumentIngestionResult,
    DocumentTypeValidation,
    build_document_services,
)


def test_document_service_ingest_with_validation_reports_match(
    tmp_path: Path,
):
    from documents import DocumentArtifact

    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "hello nexus",
        encoding="utf-8",
    )

    services = build_document_services()

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path)
        )
    )

    document = services.document_service.create_document(
        name="document.txt",
        mime_type="text/plain",
        source=str(file_path),
        artifact_id=artifact.id,
    )

    result = (
        services.document_service
        .ingest_with_validation(document)
    )

    assert isinstance(
        result,
        DocumentIngestionResult,
    )

    assert isinstance(
        result.type_validation,
        DocumentTypeValidation,
    )

    assert result.type_matches
    assert not result.type_mismatch
    assert result.content is not None
    assert result.content.text == "hello nexus"


def test_document_service_ingest_with_validation_reports_mismatch(
    tmp_path: Path,
):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "hello nexus",
        encoding="utf-8",
    )

    services = build_document_services()

    from documents import DocumentArtifact

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path)
        )
    )

    document = services.document_service.create_document(
        name="document.txt",
        mime_type="application/pdf",
        source=str(file_path),
        artifact_id=artifact.id,
    )

    result = (
        services.document_service
        .ingest_with_validation(document)
    )

    assert isinstance(
        result,
        DocumentIngestionResult,
    )

    assert result.type_validation is not None
    assert result.type_mismatch
    assert not result.type_matches

    assert (
        result.type_validation.declared_type.mime_type
        == "application/pdf"
    )

    assert (
        result.type_validation.detected_type.mime_type
        == "text/plain"
    )

    assert result.content is not None
    assert result.content.text == "hello nexus"


def test_document_service_ingest_preserves_legacy_contract(
    tmp_path: Path,
):
    file_path = tmp_path / "document.txt"
    file_path.write_text(
        "legacy contract",
        encoding="utf-8",
    )

    services = build_document_services()

    from documents import DocumentArtifact

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path)
        )
    )

    document = services.document_service.create_document(
        name="document.txt",
        mime_type="text/plain",
        source=str(file_path),
        artifact_id=artifact.id,
    )

    resolution = services.document_service.ingest(
        document
    )

    assert resolution.document.id == document.id
    assert resolution.artifact is not None
    assert resolution.content is not None
    assert resolution.content.text == "legacy contract"
