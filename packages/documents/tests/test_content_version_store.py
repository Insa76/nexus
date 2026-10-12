from documents.content_version import DocumentContentVersion
from documents.content_version_store import DocumentContentVersionStore


def create_version(
    document_id: str,
    content_id: str,
    version: int,
) -> DocumentContentVersion:
    return DocumentContentVersion.create(
        document_id=document_id,
        content_id=content_id,
        version=version,
        content_type="text/plain",
    )


def test_store_add_and_get():
    store = DocumentContentVersionStore()

    version = create_version(
        "document-1",
        "content-1",
        1,
    )

    stored = store.add(version)

    assert stored is version
    assert store.get(version.id) is version


def test_store_list():
    store = DocumentContentVersionStore()

    version_1 = create_version(
        "document-1",
        "content-1",
        1,
    )
    version_2 = create_version(
        "document-1",
        "content-2",
        2,
    )

    store.add(version_1)
    store.add(version_2)

    assert store.list() == [
        version_1,
        version_2,
    ]


def test_store_list_for_document():
    store = DocumentContentVersionStore()

    document_1_version = create_version(
        "document-1",
        "content-1",
        1,
    )
    document_2_version = create_version(
        "document-2",
        "content-2",
        1,
    )

    store.add(document_1_version)
    store.add(document_2_version)

    assert store.list_for_document("document-1") == [
        document_1_version,
    ]


def test_store_get_latest_for_document():
    store = DocumentContentVersionStore()

    version_1 = create_version(
        "document-1",
        "content-1",
        1,
    )
    version_3 = create_version(
        "document-1",
        "content-3",
        3,
    )
    version_2 = create_version(
        "document-1",
        "content-2",
        2,
    )

    store.add(version_1)
    store.add(version_3)
    store.add(version_2)

    assert store.get_latest_for_document(
        "document-1"
    ) is version_3


def test_store_latest_returns_none_for_unknown_document():
    store = DocumentContentVersionStore()

    assert (
        store.get_latest_for_document("unknown")
        is None
    )


def test_store_remove():
    store = DocumentContentVersionStore()

    version = create_version(
        "document-1",
        "content-1",
        1,
    )

    store.add(version)

    assert store.remove(version.id) is version
    assert store.get(version.id) is None


def test_store_clear():
    store = DocumentContentVersionStore()

    version = create_version(
        "document-1",
        "content-1",
        1,
    )

    store.add(version)
    store.clear()

    assert store.count() == 0
    assert store.list() == []


def test_store_count():
    store = DocumentContentVersionStore()

    store.add(
        create_version(
            "document-1",
            "content-1",
            1,
        )
    )
    store.add(
        create_version(
            "document-1",
            "content-2",
            2,
        )
    )

    assert store.count() == 2

def test_store_get_next_version_starts_at_one():
    store = DocumentContentVersionStore()

    assert (
        store.get_next_version("document-1")
        == 1
    )


def test_store_get_next_version_returns_next_number():
    store = DocumentContentVersionStore()

    store.add(
        create_version(
            "document-1",
            "content-1",
            1,
        )
    )

    assert (
        store.get_next_version("document-1")
        == 2
    )


def test_store_get_next_version_uses_highest_version():
    store = DocumentContentVersionStore()

    store.add(
        create_version(
            "document-1",
            "content-1",
            1,
        )
    )

    store.add(
        create_version(
            "document-1",
            "content-3",
            3,
        )
    )

    store.add(
        create_version(
            "document-1",
            "content-2",
            2,
        )
    )

    assert (
        store.get_next_version("document-1")
        == 4
    )


def test_store_get_next_version_is_independent_per_document():
    store = DocumentContentVersionStore()

    store.add(
        create_version(
            "document-1",
            "content-1",
            1,
        )
    )

    store.add(
        create_version(
            "document-1",
            "content-2",
            2,
        )
    )

    store.add(
        create_version(
            "document-2",
            "content-1",
            1,
        )
    )

    assert (
        store.get_next_version("document-1")
        == 3
    )

    assert (
        store.get_next_version("document-2")
        == 2
    )
