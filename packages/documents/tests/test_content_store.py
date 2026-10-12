import pytest

from documents import ContentStore, DocumentContent


def test_add_and_get_content():
    store = ContentStore()

    content = DocumentContent.create(
        text="Contenido del documento.",
    )

    result = store.add(content)

    assert result is content
    assert store.get(content.id) is content


def test_get_unknown_content_returns_none():
    store = ContentStore()

    assert store.get("missing") is None


def test_list_contents():
    store = ContentStore()

    first = DocumentContent.create(
        text="Primer contenido.",
    )
    second = DocumentContent.create(
        text="Segundo contenido.",
    )

    store.add(first)
    store.add(second)

    assert store.list() == [first, second]


def test_update_content():
    store = ContentStore()

    content = DocumentContent.create(
        text="Contenido original.",
    )
    store.add(content)

    updated = DocumentContent(
        id=content.id,
        text="Contenido actualizado.",
        content_type=content.content_type,
        language=content.language,
        created_at=content.created_at,
    )

    result = store.update(updated)

    assert result is updated
    assert store.get(content.id) is updated


def test_update_unknown_content_raises():
    store = ContentStore()

    content = DocumentContent.create(
        text="Contenido.",
    )

    with pytest.raises(KeyError, match="Content not found"):
        store.update(content)


def test_remove_content():
    store = ContentStore()

    content = DocumentContent.create(
        text="Contenido.",
    )
    store.add(content)

    result = store.remove(content.id)

    assert result is content
    assert store.get(content.id) is None


def test_remove_unknown_content_returns_none():
    store = ContentStore()

    assert store.remove("missing") is None


def test_clear_contents():
    store = ContentStore()

    store.add(
        DocumentContent.create(
            text="Primer contenido.",
        )
    )
    store.add(
        DocumentContent.create(
            text="Segundo contenido.",
        )
    )

    store.clear()

    assert store.list() == []
    assert store.count() == 0


def test_count_contents():
    store = ContentStore()

    assert store.count() == 0

    store.add(
        DocumentContent.create(
            text="Contenido.",
        )
    )

    assert store.count() == 1
