from documents import Document, DocumentArtifact


def test_document_can_reference_artifact():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        artifact_id=artifact.id,
    )

    assert document.artifact_id == artifact.id


def test_document_artifact_reference_is_optional():
    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
    )

    assert document.artifact_id is None


def test_document_keeps_artifact_reference_immutable():
    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        artifact_id=artifact.id,
    )

    try:
        document.artifact_id = "another-artifact"
    except AttributeError:
        pass
    else:
        raise AssertionError("Document should be immutable")
