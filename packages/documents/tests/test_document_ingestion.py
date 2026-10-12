from documents import (
    DocumentArtifact,
    DocumentContent,
    DocumentIngestor,
    IngestionResult,
)


class FakeIngestor:
    def ingest(self, artifact: DocumentArtifact) -> IngestionResult:
        content = DocumentContent.create(
            text="Contenido extraído.",
            content_type="text/plain",
            language="es",
        )

        return IngestionResult(
            artifact=artifact,
            content=content,
        )


def test_ingestion_result_contains_artifact_and_content():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.txt",
    )

    content = DocumentContent.create(
        text="Contenido.",
    )

    result = IngestionResult(
        artifact=artifact,
        content=content,
    )

    assert result.artifact is artifact
    assert result.content is content


def test_ingestor_protocol_can_be_implemented():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.txt",
    )

    ingestor = FakeIngestor()

    result = ingestor.ingest(artifact)

    assert isinstance(result, IngestionResult)
    assert result.artifact is artifact
    assert result.content.text == "Contenido extraído."


def test_ingestion_result_is_immutable():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.txt",
    )

    content = DocumentContent.create(
        text="Contenido.",
    )

    result = IngestionResult(
        artifact=artifact,
        content=content,
    )

    try:
        result.content = content
    except AttributeError:
        pass
    else:
        raise AssertionError("IngestionResult should be immutable")


def test_document_ingestor_protocol_is_runtime_importable():
    assert DocumentIngestor is not None
