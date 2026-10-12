from documents import DocumentMetadata


def test_metadata_defaults_are_empty():
    metadata = DocumentMetadata()

    assert metadata.filename is None
    assert metadata.title is None
    assert metadata.author is None
    assert metadata.language is None
    assert metadata.document_type is None
    assert metadata.tags == ()
    assert metadata.extra == {}


def test_metadata_to_dict():
    metadata = DocumentMetadata(
        filename="manual.pdf",
        title="Manual",
        author="NEXUS",
        language="es",
        document_type="pdf",
        tags=("manual", "technical"),
        extra={"department": "operations"},
    )

    data = metadata.to_dict()

    assert data["filename"] == "manual.pdf"
    assert data["title"] == "Manual"
    assert data["author"] == "NEXUS"
    assert data["language"] == "es"
    assert data["document_type"] == "pdf"
    assert data["tags"] == ("manual", "technical")
    assert data["extra"] == {"department": "operations"}


def test_metadata_from_dict():
    metadata = DocumentMetadata.from_dict(
        {
            "filename": "manual.pdf",
            "title": "Manual",
            "language": "es",
            "tags": ["manual", "technical"],
            "department": "operations",
        }
    )

    assert metadata.filename == "manual.pdf"
    assert metadata.title == "Manual"
    assert metadata.language == "es"
    assert metadata.tags == ("manual", "technical")
    assert metadata.extra == {"department": "operations"}


def test_metadata_from_dict_preserves_unknown_fields_as_extra():
    metadata = DocumentMetadata.from_dict(
        {
            "filename": "guide.pdf",
            "custom_field": "value",
        }
    )

    assert metadata.filename == "guide.pdf"
    assert metadata.extra == {
        "custom_field": "value",
    }


def test_metadata_is_immutable():
    metadata = DocumentMetadata(
        filename="guide.pdf",
        language="es",
    )

    try:
        metadata.filename = "other.pdf"
    except AttributeError:
        pass
    else:
        raise AssertionError("DocumentMetadata should be immutable")
