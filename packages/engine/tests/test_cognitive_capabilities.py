
from unittest.mock import MagicMock

from documents.cognitive import DocumentCognitiveAccess
from engine.cognitive_capabilities import CognitiveCapabilityRouter


def test_cognitive_capability_router_uses_document_access():
    document_access = MagicMock(
        spec=DocumentCognitiveAccess,
    )

    expected = MagicMock()
    context = MagicMock()
    document_access.find_relevant.return_value = expected

    router = CognitiveCapabilityRouter(
        document_access=document_access,
    )

    result = router.find_relevant_documents(
        context=context,
        name="manual.pdf",
        mime_type="application/pdf",
        offset=0,
        limit=5,
    )

    assert result is expected

    document_access.find_relevant.assert_called_once_with(
        context=context,
        name="manual.pdf",
        mime_type="application/pdf",
        offset=0,
        limit=5,
    )
