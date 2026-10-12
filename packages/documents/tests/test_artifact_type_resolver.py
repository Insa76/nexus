import pytest

from documents import (
    ArtifactTypeResolver,
    DocumentArtifact,
)


def test_resolves_txt_artifact():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.txt",
    )

    document_type = resolver.resolve(
        artifact
    )

    assert document_type.mime_type == "text/plain"


def test_resolves_markdown_artifact():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/readme.md",
    )

    document_type = resolver.resolve(
        artifact
    )

    assert document_type.mime_type == "text/markdown"


def test_resolves_json_artifact():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/data.json",
    )

    document_type = resolver.resolve(
        artifact
    )

    assert document_type.mime_type == "application/json"


def test_resolves_pdf_artifact():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.pdf",
    )

    document_type = resolver.resolve(
        artifact
    )

    assert document_type.mime_type == "application/pdf"


def test_resolves_extension_case_insensitively():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/MANUAL.PDF",
    )

    document_type = resolver.resolve(
        artifact
    )

    assert document_type.mime_type == "application/pdf"


def test_rejects_empty_location():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="   ",
    )

    with pytest.raises(ValueError):
        resolver.resolve(
            artifact
        )


def test_rejects_unknown_extension():
    resolver = ArtifactTypeResolver()

    artifact = DocumentArtifact.create(
        location="C:/documents/manual.xyz",
    )

    with pytest.raises(ValueError):
        resolver.resolve(
            artifact
        )
