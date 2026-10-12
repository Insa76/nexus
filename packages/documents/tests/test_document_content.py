from datetime import timezone

from documents import Document, DocumentContent


def test_content_create():
    content = DocumentContent.create(
        text="Contenido del documento.",
    )

    assert content.id
    assert content.text == "Contenido del documento."
    assert content.content_type == "text/plain"
    assert content.language is None
    assert content.created_at.tzinfo == timezone.utc


def test_content_create_with_metadata():
    content = DocumentContent.create(
        text="Contenido en español.",
        content_type="text/markdown",
        language="es",
    )

    assert content.text == "Contenido en español."
    assert content.content_type == "text/markdown"
    assert content.language == "es"


def test_content_is_immutable():
    content = DocumentContent.create(
        text="Contenido.",
    )

    try:
        content.text = "Otro contenido."
    except AttributeError:
        pass
    else:
        raise AssertionError("DocumentContent should be immutable")


def test_document_can_reference_content():
    content = DocumentContent.create(
        text="Contenido del contrato.",
    )

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        content_id=content.id,
    )

    assert document.content_id == content.id


def test_document_content_reference_is_optional():
    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
    )

    assert document.content_id is None


def test_document_content_reference_is_immutable():
    content = DocumentContent.create(
        text="Contenido.",
    )

    document = Document.create(
        name="Contrato.pdf",
        mime_type="application/pdf",
        source="local",
        content_id=content.id,
    )

    try:
        document.content_id = "another-content"
    except AttributeError:
        pass
    else:
        raise AssertionError("Document should be immutable")
