from unittest.mock import MagicMock

from documents.capability import DocumentCapability
from documents.cognitive import DocumentCognitiveAccess
from documents.models import Document
from documents.query import DocumentQueryResult


def test_document_cognitive_access_finds_relevant_documents():
    capability = MagicMock(spec=DocumentCapability)

    document = MagicMock(spec=Document)

    query = MagicMock(spec=DocumentQueryResult)
    capability.query.return_value = query
    capability.relevant_documents.return_value = (document,)

    access = DocumentCognitiveAccess(capability)

    result = access.find_relevant(
        context=MagicMock(),
        name="manual.pdf",
        mime_type="application/pdf",
        offset=0,
        limit=10,
    )

    capability.query.assert_called_once_with(
        context=result.query and capability.query.call_args.kwargs["context"],
        name="manual.pdf",
        mime_type="application/pdf",
        offset=0,
        limit=10,
    )

    capability.relevant_documents.assert_called_once()

    assert result.query is query
    assert result.documents == (document,)
    assert result.metadata["operation"] == "find_relevant"
    assert result.metadata["name"] == "manual.pdf"
    assert result.metadata["mime_type"] == "application/pdf"
    assert result.metadata["count"] == 1
