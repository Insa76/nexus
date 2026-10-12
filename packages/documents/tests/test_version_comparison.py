from documents import (
    DocumentContentVersion,
    DocumentContentVersionStore,
    DocumentVersionComparator,
    DocumentVersionResolver,
)


def add_version(
    store: DocumentContentVersionStore,
    document_id: str,
    version: int,
    content_id: str,
) -> DocumentContentVersion:
    content_version = DocumentContentVersion.create(
        document_id=document_id,
        content_id=content_id,
        version=version,
        content_type="text/plain",
    )
    store.add(content_version)
    return content_version


def build_resolution(
    document_id: str = "doc-1",
    from_version: int = 1,
    from_content_id: str = "content-1",
    to_version: int = 2,
    to_content_id: str = "content-2",
):
    store = DocumentContentVersionStore()

    add_version(
        store,
        document_id=document_id,
        version=from_version,
        content_id=from_content_id,
    )

    add_version(
        store,
        document_id=document_id,
        version=to_version,
        content_id=to_content_id,
    )

    resolver = DocumentVersionResolver(store)

    return resolver.resolve_pair(
        document_id=document_id,
        from_version=from_version,
        to_version=to_version,
    )


def test_comparator_detects_changed_content():
    resolution = build_resolution(
        from_content_id="content-1",
        to_content_id="content-2",
    )

    comparator = DocumentVersionComparator()

    result = comparator.compare(resolution)

    assert result.document_id == "doc-1"
    assert result.from_version == 1
    assert result.to_version == 2
    assert result.from_content_id == "content-1"
    assert result.to_content_id == "content-2"
    assert result.changed is True
    assert result.unchanged is False


def test_comparator_detects_unchanged_content():
    resolution = build_resolution(
        from_content_id="content-1",
        to_content_id="content-1",
    )

    comparator = DocumentVersionComparator()

    result = comparator.compare(resolution)

    assert result.changed is False
    assert result.unchanged is True


def test_comparator_preserves_document_identity():
    resolution = build_resolution(
        document_id="contract-123",
    )

    comparator = DocumentVersionComparator()

    result = comparator.compare(resolution)

    assert result.document_id == "contract-123"


def test_comparator_preserves_version_numbers():
    resolution = build_resolution(
        from_version=3,
        from_content_id="content-3",
        to_version=7,
        to_content_id="content-7",
    )

    comparator = DocumentVersionComparator()

    result = comparator.compare(resolution)

    assert result.from_version == 3
    assert result.to_version == 7


def test_comparator_preserves_content_ids():
    resolution = build_resolution(
        from_content_id="content-before",
        to_content_id="content-after",
    )

    comparator = DocumentVersionComparator()

    result = comparator.compare(resolution)

    assert result.from_content_id == "content-before"
    assert result.to_content_id == "content-after"


def test_comparator_is_deterministic():
    resolution = build_resolution(
        from_content_id="content-a",
        to_content_id="content-b",
    )

    comparator = DocumentVersionComparator()

    first = comparator.compare(resolution)
    second = comparator.compare(resolution)

    assert first == second
