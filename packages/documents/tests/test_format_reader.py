from documents import (
    DocumentArtifact,
    DocumentType,
    LocalArtifactReader,
    TextFormatReader,
)


def test_text_format_reader_supports_text_plain():
    reader = TextFormatReader(
        artifact_reader=LocalArtifactReader()
    )

    assert reader.supports(
        DocumentType.from_mime_type(
            "text/plain"
        )
    )


def test_text_format_reader_does_not_support_pdf():
    reader = TextFormatReader(
        artifact_reader=LocalArtifactReader()
    )

    assert not reader.supports(
        DocumentType.from_mime_type(
            "application/pdf"
        )
    )


def test_text_format_reader_reads_text(
    tmp_path,
):
    path = tmp_path / "document.txt"

    path.write_text(
        "Contenido del documento.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=str(path),
    )

    reader = TextFormatReader(
        artifact_reader=LocalArtifactReader()
    )

    result = reader.read(
        artifact,
        DocumentType.from_mime_type(
            "text/plain"
        ),
    )

    assert result == "Contenido del documento."


def test_text_format_reader_rejects_unsupported_type(
    tmp_path,
):
    path = tmp_path / "document.txt"

    path.write_text(
        "Contenido.",
        encoding="utf-8",
    )

    artifact = DocumentArtifact.create(
        location=str(path),
    )

    reader = TextFormatReader(
        artifact_reader=LocalArtifactReader()
    )

    try:
        reader.read(
            artifact,
            DocumentType.from_mime_type(
                "application/pdf"
            ),
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for unsupported type"
    )
