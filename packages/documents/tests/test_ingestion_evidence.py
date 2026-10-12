from pathlib import Path

from documents import (
    DocumentArtifact,
    DocumentIngestionResult,
    build_document_services,
)


def test_document_ingestion_exposes_detection_strategy(
    tmp_path: Path,
):
    file_path = tmp_path / "manual.txt"

    file_path.write_text(
        "nexus evidence",
        encoding="utf-8",
    )

    services = build_document_services()

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path),
        )
    )

    document = services.document_service.create_document(
        name="manual.txt",
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

    assert result.detection_evidence is not None

    assert (
        result.detection_evidence.detected_type.mime_type
        == "text/plain"
    )

    assert (
        result.detection_strategy
        == "ExtensionTypeDetectionStrategy"
    )


def test_document_ingestion_exposes_detection_and_validation(
    tmp_path: Path,
):
    file_path = tmp_path / "manual.txt"

    file_path.write_text(
        "nexus mismatch evidence",
        encoding="utf-8",
    )

    services = build_document_services()

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path),
        )
    )

    document = services.document_service.create_document(
        name="manual.txt",
        mime_type="application/pdf",
        source=str(file_path),
        artifact_id=artifact.id,
    )

    result = (
        services.document_service
        .ingest_with_validation(document)
    )

    assert result.detection_strategy == (
        "ExtensionTypeDetectionStrategy"
    )

    assert result.detected_type.mime_type == (
        "text/plain"
    )

    assert result.type_mismatch

    assert result.content is not None
    assert result.content.text == (
        "nexus mismatch evidence"
    )

def test_document_persists_ingestion_evidence(
    tmp_path: Path,
):
    from documents import DocumentIngestionEvidence

    file_path = tmp_path / "manual.txt"

    file_path.write_text(
        "persistent evidence",
        encoding="utf-8",
    )

    services = build_document_services()

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path),
        )
    )

    document = services.document_service.create_document(
        name="manual.txt",
        mime_type="text/plain",
        source=str(file_path),
        artifact_id=artifact.id,
    )

    result = (
        services.document_service
        .ingest_with_validation(document)
    )

    persisted_document = (
        services.document_store.get(document.id)
    )

    assert persisted_document is not None

    assert isinstance(
        persisted_document.ingestion_evidence,
        DocumentIngestionEvidence,
    )

    assert (
        persisted_document.ingestion_evidence
        .declared_type.mime_type
        == "text/plain"
    )

    assert (
        persisted_document.ingestion_evidence
        .detected_type.mime_type
        == "text/plain"
    )

    assert (
        persisted_document.ingestion_evidence
        .detection_strategy
        == "ExtensionTypeDetectionStrategy"
    )

    assert (
        persisted_document.ingestion_evidence.matches
    )

    assert result.document.id == document.id


def test_document_persists_type_mismatch_evidence(
    tmp_path: Path,
):
    from documents import DocumentIngestionEvidence

    file_path = tmp_path / "manual.txt"

    file_path.write_text(
        "mismatch evidence",
        encoding="utf-8",
    )

    services = build_document_services()

    artifact = services.document_service.add_artifact(
        DocumentArtifact.create(
            location=str(file_path),
        )
    )

    document = services.document_service.create_document(
        name="manual.txt",
        mime_type="application/pdf",
        source=str(file_path),
        artifact_id=artifact.id,
    )

    services.document_service.ingest_with_validation(
        document
    )

    persisted_document = (
        services.document_store.get(document.id)
    )

    assert persisted_document is not None
    assert persisted_document.ingestion_evidence is not None

    evidence = (
        persisted_document.ingestion_evidence
    )

    assert (
        evidence.declared_type.mime_type
        == "application/pdf"
    )

    assert (
        evidence.detected_type.mime_type
        == "text/plain"
    )

    assert evidence.mismatch
    assert not evidence.matches
