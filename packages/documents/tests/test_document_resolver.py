from documents import (
    ArtifactStore,
    ContentStore,
    Document,
    DocumentArtifact,
    DocumentContent,
    DocumentResolver,
    DocumentStore,
)


def test_resolve_document_with_artifact_and_content():
    document_store = DocumentStore()
    artifact_store = ArtifactStore()
    content_store = ContentStore()

    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )
    artifact_store.add(artifact)

    content = DocumentContent.create(
        text="Contenido del contrato.",
        language="es",
    )
    content_store.add(content)

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        artifact_id=artifact.id,
        content_id=content.id,
    )
    document_store.add(document)

    resolver = DocumentResolver(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
    )

    result = resolver.resolve(document.id)

    assert result is not None
    assert result.document is document
    assert result.artifact is artifact
    assert result.content is content


def test_resolve_document_without_artifact_or_content():
    document_store = DocumentStore()
    artifact_store = ArtifactStore()
    content_store = ContentStore()

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
    )
    document_store.add(document)

    resolver = DocumentResolver(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
    )

    result = resolver.resolve(document.id)

    assert result is not None
    assert result.document is document
    assert result.artifact is None
    assert result.content is None


def test_resolve_document_with_missing_artifact():
    document_store = DocumentStore()
    artifact_store = ArtifactStore()
    content_store = ContentStore()

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        artifact_id="missing-artifact",
    )
    document_store.add(document)

    resolver = DocumentResolver(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
    )

    result = resolver.resolve(document.id)

    assert result is not None
    assert result.document is document
    assert result.artifact is None
    assert result.content is None


def test_resolve_document_with_missing_content():
    document_store = DocumentStore()
    artifact_store = ArtifactStore()
    content_store = ContentStore()

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        content_id="missing-content",
    )
    document_store.add(document)

    resolver = DocumentResolver(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
    )

    result = resolver.resolve(document.id)

    assert result is not None
    assert result.document is document
    assert result.artifact is None
    assert result.content is None


def test_resolve_document_without_content_store():
    document_store = DocumentStore()
    artifact_store = ArtifactStore()

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        content_id="content-1",
    )
    document_store.add(document)

    resolver = DocumentResolver(
        document_store=document_store,
        artifact_store=artifact_store,
    )

    result = resolver.resolve(document.id)

    assert result is not None
    assert result.document is document
    assert result.artifact is None
    assert result.content is None


def test_resolve_unknown_document_returns_none():
    document_store = DocumentStore()
    artifact_store = ArtifactStore()
    content_store = ContentStore()

    resolver = DocumentResolver(
        document_store=document_store,
        artifact_store=artifact_store,
        content_store=content_store,
    )

    assert resolver.resolve("missing-document") is None
