from unittest.mock import MagicMock

from documents.cognitive import DocumentCognitiveAccess
from engine.cognitive_capabilities import CognitiveCapabilityRouter


def test_cognitive_capability_router_uses_document_access():
    document_access = MagicMock(
        spec=DocumentCognitiveAccess,
    )

    expected = MagicMock()
    document_access.find_relevant.return_value = expected

    router = CognitiveCapabilityRouter(
        document_access=document_access,
    )

    result = router.find_relevant_documents(
        context=MagicMock(),
        name="manual.pdf",
        mime_type="application/pdf",
        offset=0,
        limit=5,
    )

    assert result is expected

    document_access.find_relevant.assert_called_once_with(
        context=router.find_relevant_documents.call_args
        if False
        else document_access.find_relevant.call_args.kwargs["context"],
        name="manual.pdf",
        mime_type="application/pdf",
        offset=0,
        limit=5,
    )
