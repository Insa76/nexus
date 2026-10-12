import pytest

from documents import (
    DocumentType,
    FormatReaderRegistry,
)


class FakeFormatReader:
    def supports(self, document_type):
        return True

    def read(self, artifact, document_type):
        return "content"


def test_registry_registers_reader():
    registry = FormatReaderRegistry()
    reader = FakeFormatReader()

    registry.register(
        "text/plain",
        reader,
    )

    assert registry.get(
        "text/plain"
    ) is reader


def test_registry_accepts_document_type():
    registry = FormatReaderRegistry()
    reader = FakeFormatReader()

    registry.register(
        DocumentType.from_mime_type(
            "TEXT/PLAIN"
        ),
        reader,
    )

    assert registry.get(
        "text/plain"
    ) is reader


def test_registry_normalizes_mime_type():
    registry = FormatReaderRegistry()
    reader = FakeFormatReader()

    registry.register(
        " TEXT/PLAIN ",
        reader,
    )

    assert registry.supports(
        "text/plain"
    )


def test_registry_supports_document_type():
    registry = FormatReaderRegistry()
    reader = FakeFormatReader()

    registry.register(
        "application/pdf",
        reader,
    )

    assert registry.supports(
        DocumentType.from_mime_type(
            "APPLICATION/PDF"
        )
    )


def test_registry_removes_reader():
    registry = FormatReaderRegistry()
    reader = FakeFormatReader()

    registry.register(
        "text/plain",
        reader,
    )

    removed = registry.remove(
        " TEXT/PLAIN "
    )

    assert removed is reader
    assert not registry.supports(
        "text/plain"
    )


def test_registry_lists_content_types():
    registry = FormatReaderRegistry()

    registry.register(
        "text/plain",
        FakeFormatReader(),
    )

    registry.register(
        "application/pdf",
        FakeFormatReader(),
    )

    assert registry.content_types() == [
        "text/plain",
        "application/pdf",
    ]


def test_registry_clear():
    registry = FormatReaderRegistry()

    registry.register(
        "text/plain",
        FakeFormatReader(),
    )

    registry.clear()

    assert registry.content_types() == []


def test_registry_rejects_invalid_document_type():
    registry = FormatReaderRegistry()

    with pytest.raises(ValueError):
        registry.register(
            "invalid",
            FakeFormatReader(),
        )
