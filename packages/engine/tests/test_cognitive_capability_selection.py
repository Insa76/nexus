from unittest.mock import MagicMock

from documents import DocumentCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityInvocation,
    CognitiveCapabilityRouter,
)


def test_router_selects_documents_capability():
    document_access = MagicMock(
        spec=DocumentCognitiveAccess,
    )

    router = CognitiveCapabilityRouter(
        document_access=document_access,
    )

    invocation = router.select(
        action="documents.find_relevant",
        parameters={
            "name": "manual.pdf",
        },
    )

    assert isinstance(
        invocation,
        CognitiveCapabilityInvocation,
    )

    assert invocation.capability == "documents"
    assert invocation.operation == "find_relevant"
    assert invocation.parameters == {
        "name": "manual.pdf",
    }


def test_router_does_not_select_unknown_capability():
    document_access = MagicMock(
        spec=DocumentCognitiveAccess,
    )

    router = CognitiveCapabilityRouter(
        document_access=document_access,
    )

    invocation = router.select(
        action="unknown.operation",
    )

    assert invocation is None
