from documents import (
    ArtifactTypeResolver,
    DocumentArtifact,
    DocumentTypeDetectionEvidence,
    ExtensionTypeDetectionStrategy,
)


def test_resolver_returns_detection_evidence():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/example.txt",
    )

    result = resolver.resolve_with_evidence(
        artifact
    )

    assert isinstance(
        result,
        DocumentTypeDetectionEvidence,
    )

    assert result.detected_type.mime_type == (
        "text/plain"
    )

    assert result.strategy == (
        "ExtensionTypeDetectionStrategy"
    )


def test_resolve_preserves_existing_contract():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/example.txt",
    )

    result = resolver.resolve(artifact)

    assert result.mime_type == "text/plain"


def test_detection_evidence_exposes_mime_type():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/example.txt",
    )

    result = resolver.resolve_with_evidence(
        artifact
    )

    assert result.mime_type == "text/plain"
