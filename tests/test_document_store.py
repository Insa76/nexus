import pytest

from documents import Document, DocumentStore


def create_document(
    name: str = "Documento.pdf",
) -> Document:
    return Document.create(
        name=name,
        mime_type="application/pdf",
        source=f"local:/documents/{name}",
    )


def test_add_and_get_document() -> None:
    store = DocumentStore()
    document = create_document()

    result = store.add(document)

    assert result == document
    assert store.get(document.id) == document


def test_get_unknown_document_returns_none() -> None:
    store = DocumentStore()

    assert store.get("unknown") is None


def test_list_documents() -> None:
    store = DocumentStore()

    first = create_document("uno.pdf")
    second = create_document("dos.pdf")

    store.add(first)
    store.add(second)

    assert store.list() == [first, second]


def test_update_document() -> None:
    store = DocumentStore()

    document = create_document()

    store.add(document)

    updated = Document(
        **{
            **document.__dict__,
            "name": "Documento actualizado.pdf",
        }
    )

    result = store.update(updated)

    assert result == updated
    assert store.get(document.id) == updated


def test_update_unknown_document_raises() -> None:
    store = DocumentStore()
    document = create_document()

    with pytest.raises(KeyError):
        store.update(document)


def test_remove_document() -> None:
    store = DocumentStore()
    document = create_document()

    store.add(document)

    result = store.remove(document.id)

    assert result == document
    assert store.get(document.id) is None


def test_remove_unknown_document_returns_none() -> None:
    store = DocumentStore()

    assert store.remove("unknown") is None


def test_clear_documents() -> None:
    store = DocumentStore()

    store.add(create_document("uno.pdf"))
    store.add(create_document("dos.pdf"))

    store.clear()

    assert store.list() == []
    assert store.count() == 0


def test_count_documents() -> None:
    store = DocumentStore()

    assert store.count() == 0

    store.add(create_document("uno.pdf"))
    store.add(create_document("dos.pdf"))

    assert store.count() == 2
