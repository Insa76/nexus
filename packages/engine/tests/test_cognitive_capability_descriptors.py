from unittest.mock import MagicMock

from documents import DocumentCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityRouter,
)


def test_router_exposes_available_cognitive_capabilities():
    access = MagicMock(spec=DocumentCognitiveAccess)

    router = CognitiveCapabilityRouter(
        document_access=access,
    )

    descriptors = router.descriptors

    assert len(descriptors) == 1

    descriptor = descriptors[0]

    assert descriptor.capability == "documents"
    assert descriptor.operation == "find_relevant"
    assert descriptor.action == "documents.find_relevant"


def test_router_exposes_no_document_capability_when_unavailable():
    router = CognitiveCapabilityRouter()

    assert router.descriptors == ()
