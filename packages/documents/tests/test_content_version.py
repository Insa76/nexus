from datetime import datetime, timezone

import pytest

from documents.content_version import DocumentContentVersion
from documents.document_type import DocumentType


def test_document_content_version_create():
    version = DocumentContentVersion.create(
        document_id="document-1",
        content_id="content-1",
        version=1,
        content_type="text/plain",
    )

    assert version.id
    assert version.document_id == "document-1"
    assert version.content_id == "content-1"
    assert version.version == 1
    assert version.content_type.mime_type == "text/plain"
    assert isinstance(version.created_at, datetime)
    assert version.created_at.tzinfo == timezone.utc


def test_document_content_version_accepts_document_type():
    document_type = DocumentType.from_mime_type(
        "text/plain"
    )

    version = DocumentContentVersion.create(
        document_id="document-1",
        content_id="content-1",
        version=2,
        content_type=document_type,
    )

    assert version.content_type is document_type


def test_document_content_version_rejects_zero_version():
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        DocumentContentVersion.create(
            document_id="document-1",
            content_id="content-1",
            version=0,
            content_type="text/plain",
        )


def test_document_content_version_rejects_negative_version():
    with pytest.raises(
        ValueError,
        match="greater than zero",
    ):
        DocumentContentVersion.create(
            document_id="document-1",
            content_id="content-1",
            version=-1,
            content_type="text/plain",
        )


def test_document_content_version_is_immutable():
    version = DocumentContentVersion.create(
        document_id="document-1",
        content_id="content-1",
        version=1,
        content_type="text/plain",
    )

    with pytest.raises(AttributeError):
        version.version = 2
