import pytest

from documents import (
    DocumentContentVersion,
    DocumentContentVersionStore,
    DocumentVersionResolver,
)


def build_store() -> DocumentContentVersionStore:
    return DocumentContentVersionStore()


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


def test_resolver_returns_specific_version():
    store = build_store()

    v1 = add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    add_version(
        store,
        document_id="doc-1",
        version=2,
        content_id="content-2",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_version("doc-1", 1)

    assert result == v1


def test_resolver_raises_when_version_does_not_exist():
    store = build_store()

    add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    resolver = DocumentVersionResolver(store)

    with pytest.raises(
        ValueError,
        match="Document content version not found: doc-1 v2",
    ):
        resolver.resolve_version("doc-1", 2)


def test_resolver_returns_latest_version():
    store = build_store()

    add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    v2 = add_version(
        store,
        document_id="doc-1",
        version=2,
        content_id="content-2",
    )

    v3 = add_version(
        store,
        document_id="doc-1",
        version=3,
        content_id="content-3",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_latest("doc-1")

    assert result == v3
    assert result != v2


def test_resolver_raises_when_document_has_no_versions():
    store = build_store()
    resolver = DocumentVersionResolver(store)

    with pytest.raises(
        ValueError,
        match="No content versions found for document: doc-1",
    ):
        resolver.resolve_latest("doc-1")


def test_resolver_returns_previous_version():
    store = build_store()

    v1 = add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    add_version(
        store,
        document_id="doc-1",
        version=2,
        content_id="content-2",
    )

    add_version(
        store,
        document_id="doc-1",
        version=3,
        content_id="content-3",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_previous("doc-1", version=3)

    assert result.version == 2
    assert result.content_id == "content-2"


def test_resolver_previous_defaults_to_latest():
    store = build_store()

    add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    v2 = add_version(
        store,
        document_id="doc-1",
        version=2,
        content_id="content-2",
    )

    add_version(
        store,
        document_id="doc-1",
        version=3,
        content_id="content-3",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_previous("doc-1")

    assert result == v2


def test_resolver_raises_when_previous_version_does_not_exist():
    store = build_store()

    add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    resolver = DocumentVersionResolver(store)

    with pytest.raises(
        ValueError,
        match="No previous content version found for document: doc-1 v1",
    ):
        resolver.resolve_previous("doc-1", version=1)


def test_resolver_builds_explicit_version_pair():
    store = build_store()

    v1 = add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    v2 = add_version(
        store,
        document_id="doc-1",
        version=2,
        content_id="content-2",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_pair(
        document_id="doc-1",
        from_version=1,
        to_version=2,
    )

    assert result.document_id == "doc-1"
    assert result.from_version == v1
    assert result.to_version == v2


def test_resolver_builds_latest_pair():
    store = build_store()

    v1 = add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    v2 = add_version(
        store,
        document_id="doc-1",
        version=2,
        content_id="content-2",
    )

    add_version(
        store,
        document_id="doc-1",
        version=3,
        content_id="content-3",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_latest_pair("doc-1")

    assert result.document_id == "doc-1"
    assert result.from_version == v2
    assert result.to_version.version == 3
    assert result.to_version != v1


def test_resolver_rejects_same_version_pair():
    store = build_store()

    add_version(
        store,
        document_id="doc-1",
        version=1,
        content_id="content-1",
    )

    resolver = DocumentVersionResolver(store)

    with pytest.raises(
        ValueError,
        match="Cannot resolve a version comparison pair with the same version",
    ):
        resolver.resolve_pair(
            document_id="doc-1",
            from_version=1,
            to_version=1,
        )


def test_resolver_does_not_mix_versions_between_documents():
    store = build_store()

    doc_a_v1 = add_version(
        store,
        document_id="doc-a",
        version=1,
        content_id="content-a-1",
    )

    add_version(
        store,
        document_id="doc-b",
        version=1,
        content_id="content-b-1",
    )

    resolver = DocumentVersionResolver(store)

    result = resolver.resolve_version("doc-a", 1)

    assert result == doc_a_v1
    assert result.document_id == "doc-a"
