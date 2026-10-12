from datetime import timezone

from documents import DocumentArtifact


def test_artifact_create():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )

    assert artifact.id
    assert artifact.location == "local:/documents/contrato.pdf"
    assert artifact.size is None
    assert artifact.checksum is None
    assert artifact.checksum_algorithm is None
    assert artifact.created_at.tzinfo == timezone.utc


def test_artifact_create_with_physical_metadata():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
        size=2048,
        checksum="abc123",
        checksum_algorithm="sha256",
    )

    assert artifact.location == "local:/documents/contrato.pdf"
    assert artifact.size == 2048
    assert artifact.checksum == "abc123"
    assert artifact.checksum_algorithm == "sha256"


def test_artifact_is_immutable():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )

    try:
        artifact.location = "local:/documents/otro.pdf"
    except AttributeError:
        pass
    else:
        raise AssertionError("DocumentArtifact should be immutable")


def test_artifact_metadata_is_optional():
    artifact = DocumentArtifact.create(
        location="https://example.com/document.pdf",
    )

    assert artifact.size is None
    assert artifact.checksum is None
    assert artifact.checksum_algorithm is None
