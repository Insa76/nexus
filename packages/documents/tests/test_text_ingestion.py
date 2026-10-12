from documents import (
    DocumentArtifact,
    IngestionResult,
    TextIngestor,
)


class FakeArtifactReader:
    def __init__(self, text: str) -> None:
        self.text = text
        self.received_artifact = None

    def read(self, artifact: DocumentArtifact) -> str:
        self.received_artifact = artifact
        return self.text


def test_text_ingestor_reads_artifact_and_creates_content():
    artifact = DocumentArtifact.create(
        location="local:/documents/notes.txt",
    )

    reader = FakeArtifactReader(
        "Este es el contenido del documento.",
    )

    ingestor = TextIngestor(reader)

    result = ingestor.ingest(artifact)

    assert isinstance(result, IngestionResult)
    assert result.artifact is artifact
    assert result.content.text == "Este es el contenido del documento."
    assert result.content.content_type == "text/plain"
    assert reader.received_artifact is artifact


def test_text_ingestor_preserves_empty_text():
    artifact = DocumentArtifact.create(
        location="local:/documents/empty.txt",
    )

    reader = FakeArtifactReader("")

    result = TextIngestor(reader).ingest(artifact)

    assert result.content.text == ""
    assert result.content.content_type == "text/plain"
