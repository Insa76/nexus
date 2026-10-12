from unittest.mock import MagicMock

from documents import DocumentCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityInvocation,
    CognitiveCapabilityRouter,
)


def test_router_invokes_selected_documents_capability():
    document_access = MagicMock(
        spec=DocumentCognitiveAccess,
    )

    expected_result = MagicMock()
    document_access.find_relevant.return_value = expected_result

    router = CognitiveCapabilityRouter(
        document_access=document_access,
    )

    invocation = CognitiveCapabilityInvocation(
        capability="documents",
        operation="find_relevant",
        parameters={
            "name": "manual.pdf",
            "mime_type": "application/pdf",
            "offset": 2,
            "limit": 5,
        },
    )

    result = router.invoke(
        invocation,
        context={"user": "test"},
    )

    assert result is expected_result

    document_access.find_relevant.assert_called_once_with(
        context={"user": "test"},
        name="manual.pdf",
        mime_type="application/pdf",
        offset=2,
        limit=5,
    )
