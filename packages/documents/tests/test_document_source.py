import pytest

from documents import DocumentSource


def test_document_source_parses_local_source():
    source = DocumentSource.from_location(
        "local:C:/documents/test.txt"
    )

    assert source.scheme == "local"
    assert source.location == "C:/documents/test.txt"


def test_document_source_normalizes_scheme():
    source = DocumentSource.from_location(
        " LOCAL:C:/documents/test.txt "
    )

    assert source.scheme == "local"


def test_document_source_accepts_path_without_scheme():
    source = DocumentSource.from_location(
        "C:/documents/test.txt"
    )

    assert source.scheme == "local"
    assert source.location == "C:/documents/test.txt"


def test_document_source_rejects_empty_location():
    with pytest.raises(ValueError):
        DocumentSource.from_location("")


def test_document_source_rejects_missing_source_location():
    with pytest.raises(ValueError):
        DocumentSource.from_location("local:")


def test_document_source_supports_future_schemes():
    source = DocumentSource.from_location(
        "remote:documents/test.txt"
    )

    assert source.scheme == "remote"
    assert source.location == "documents/test.txt"
