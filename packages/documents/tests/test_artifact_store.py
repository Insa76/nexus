import pytest

from documents import ArtifactStore, DocumentArtifact


def test_add_and_get_artifact():
    store = ArtifactStore()

    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )

    result = store.add(artifact)

    assert result is artifact
    assert store.get(artifact.id) is artifact


def test_get_unknown_artifact_returns_none():
    store = ArtifactStore()

    assert store.get("missing") is None


def test_list_artifacts():
    store = ArtifactStore()

    first = DocumentArtifact.create(
        location="local:/documents/first.pdf",
    )
    second = DocumentArtifact.create(
        location="local:/documents/second.pdf",
    )

    store.add(first)
    store.add(second)

    assert store.list() == [first, second]


def test_update_artifact():
    store = ArtifactStore()

    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )
    store.add(artifact)

    updated = DocumentArtifact(
        id=artifact.id,
        location=artifact.location,
        size=2048,
        checksum="abc123",
        checksum_algorithm="sha256",
        created_at=artifact.created_at,
    )

    result = store.update(updated)

    assert result is updated
    assert store.get(artifact.id) is updated


def test_update_unknown_artifact_raises():
    store = ArtifactStore()

    artifact = DocumentArtifact.create(
        location="local:/documents/unknown.pdf",
    )

    with pytest.raises(KeyError, match="Artifact not found"):
        store.update(artifact)


def test_remove_artifact():
    store = ArtifactStore()

    artifact = DocumentArtifact.create(
        location="local:/documents/contrato.pdf",
    )
    store.add(artifact)

    result = store.remove(artifact.id)

    assert result is artifact
    assert store.get(artifact.id) is None


def test_remove_unknown_artifact_returns_none():
    store = ArtifactStore()

    assert store.remove("missing") is None


def test_clear_artifacts():
    store = ArtifactStore()

    store.add(
        DocumentArtifact.create(
            location="local:/documents/first.pdf",
        )
    )
    store.add(
        DocumentArtifact.create(
            location="local:/documents/second.pdf",
        )
    )

    store.clear()

    assert store.list() == []
    assert store.count() == 0


def test_count_artifacts():
    store = ArtifactStore()

    assert store.count() == 0

    store.add(
        DocumentArtifact.create(
            location="local:/documents/contrato.pdf",
        )
    )

    assert store.count() == 1
