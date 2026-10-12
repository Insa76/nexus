import pytest

from documents import (
    DocumentType,
    DocumentTypeResolver,
)


def test_document_type_normalizes_mime_type():
    document_type = DocumentType.from_mime_type(
        " TEXT/PLAIN "
    )

    assert document_type.mime_type == "text/plain"


def test_document_type_exposes_category():
    document_type = DocumentType.from_mime_type(
        "text/plain"
    )

    assert document_type.category == "text"


def test_document_type_exposes_subtype():
    document_type = DocumentType.from_mime_type(
        "application/pdf"
    )

    assert document_type.subtype == "pdf"


def test_document_type_rejects_empty_mime_type():
    with pytest.raises(ValueError):
        DocumentType.from_mime_type("")


def test_document_type_rejects_mime_type_without_separator():
    with pytest.raises(ValueError):
        DocumentType.from_mime_type(
            "application-pdf"
        )


def test_document_type_rejects_incomplete_mime_type():
    with pytest.raises(ValueError):
        DocumentType.from_mime_type(
            "application/"
        )


def test_resolver_returns_document_type():
    resolver = DocumentTypeResolver()

    result = resolver.resolve(
        "application/pdf"
    )

    assert isinstance(result, DocumentType)
    assert result.mime_type == "application/pdf"


def test_resolver_normalizes_mime_type():
    resolver = DocumentTypeResolver()

    result = resolver.resolve(
        " Application/PDF "
    )

    assert result.mime_type == "application/pdf"
