
from unittest.mock import MagicMock

from documents.capability import DocumentCapability
from documents.cognitive import DocumentCognitiveAccess
from documents.models import Document
from documents.query import DocumentQueryResult


def test_document_cognitive_access_finds_relevant_documents():
    capability = MagicMock(spec=DocumentCapability)

    document = MagicMock(spec=Document)
    query = DocumentQueryResult.from_documents(
        (document,),
        total=3,
        offset=1,
        limit=1,
    )
    capability.query.return_value = query

    access = DocumentCognitiveAccess(capability)

    result = access.find_relevant(
        context=MagicMock(),
        name="manual.pdf",
        mime_type="application/pdf",
        offset=1,
        limit=1,
    )

    capability.query.assert_called_once_with(
        context=capability.query.call_args.kwargs["context"],
        name="manual.pdf",
        mime_type="application/pdf",
        offset=1,
        limit=1,
    )

    capability.relevant_documents.assert_not_called()

    assert result.query is query
    assert result.documents == query.documents
    assert result.metadata["operation"] == "find_relevant"
    assert result.metadata["name"] == "manual.pdf"
    assert result.metadata["mime_type"] == "application/pdf"
    assert result.metadata["count"] == 1
    assert result.metadata["total"] == 3
    assert result.metadata["has_more"] is True
