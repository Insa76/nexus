from unittest.mock import MagicMock

from documents import DocumentCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityOperation,
    CognitiveCapabilityRouter,
)


def test_router_finds_operation_by_action():
    access = MagicMock(spec=DocumentCognitiveAccess)

    router = CognitiveCapabilityRouter(
        document_access=access,
    )

    assert router.find_operation(
        action="documents.find_relevant",
    ) == CognitiveCapabilityOperation(
        capability="documents",
        operation="find_relevant",
        action="documents.find_relevant",
    )


def test_router_returns_none_for_unknown_action():
    access = MagicMock(spec=DocumentCognitiveAccess)

    router = CognitiveCapabilityRouter(
        document_access=access,
    )

    assert router.find_operation(
        action="documents.unknown",
    ) is None
