from documents import (
    DocumentArtifact,
    DocumentContent,
    IngestionRegistry,
    IngestionResult,
)

from documents import DocumentType


class FakeIngestor:
    def __init__(self, label: str) -> None:
        self.label = label

    def ingest(self, artifact: DocumentArtifact) -> IngestionResult:
        return IngestionResult(
            artifact=artifact,
            content=DocumentContent.create(
                text=f"Content from {self.label}",
            ),
        )


def test_register_and_get_ingestor():
    registry = IngestionRegistry()
    ingestor = FakeIngestor("text")

    registry.register("text/plain", ingestor)

    assert registry.get("text/plain") is ingestor


def test_get_unknown_ingestor_returns_none():
    registry = IngestionRegistry()

    assert registry.get("application/pdf") is None


def test_supports_content_type():
    registry = IngestionRegistry()
    ingestor = FakeIngestor("text")

    registry.register("text/plain", ingestor)

    assert registry.supports("text/plain")
    assert not registry.supports("application/pdf")


def test_register_replaces_existing_ingestor():
    registry = IngestionRegistry()

    first = FakeIngestor("first")
    second = FakeIngestor("second")

    registry.register("text/plain", first)
    registry.register("text/plain", second)

    assert registry.get("text/plain") is second


def test_remove_ingestor():
    registry = IngestionRegistry()
    ingestor = FakeIngestor("text")

    registry.register("text/plain", ingestor)

    result = registry.remove("text/plain")

    assert result is ingestor
    assert registry.get("text/plain") is None


def test_remove_unknown_ingestor_returns_none():
    registry = IngestionRegistry()

    assert registry.remove("text/plain") is None


def test_content_types():
    registry = IngestionRegistry()

    registry.register("text/plain", FakeIngestor("text"))
    registry.register("text/markdown", FakeIngestor("markdown"))

    assert registry.content_types() == [
        "text/plain",
        "text/markdown",
    ]


def test_clear_registry():
    registry = IngestionRegistry()

    registry.register("text/plain", FakeIngestor("text"))
    registry.register("text/markdown", FakeIngestor("markdown"))

    registry.clear()

    assert registry.content_types() == []
    assert not registry.supports("text/plain")

from documents import DocumentType


def test_registry_accepts_document_type():
    registry = IngestionRegistry()

    ingestor = object()

    registry.register(
        DocumentType.from_mime_type(
            "TEXT/PLAIN"
        ),
        ingestor,
    )

    assert registry.get(
        "text/plain"
    ) is ingestor


def test_registry_normalizes_registered_mime_type():
    registry = IngestionRegistry()

    ingestor = object()

    registry.register(
        " TEXT/PLAIN ",
        ingestor,
    )

    assert registry.supports(
        "text/plain"
    )

    assert registry.supports(
        DocumentType.from_mime_type(
            "TEXT/PLAIN"
        )
    )


def test_registry_removes_normalized_type():
    registry = IngestionRegistry()

    ingestor = object()

    registry.register(
        "application/pdf",
        ingestor,
    )

    removed = registry.remove(
        DocumentType.from_mime_type(
            "APPLICATION/PDF"
        )
    )

    assert removed is ingestor
    assert not registry.supports(
        "application/pdf"
    )


def test_registry_rejects_invalid_mime_type():
    registry = IngestionRegistry()

    try:
        registry.register(
            "invalid",
            object(),
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid MIME type"
    )
