from unittest.mock import MagicMock

from documents import DocumentCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityRouter,
)


def test_router_reports_available_cognitive_capabilities():
    access = MagicMock(spec=DocumentCognitiveAccess)

    router = CognitiveCapabilityRouter(
        document_access=access,
    )

    assert router.available_capabilities() == (
        "documents",
    )


def test_router_reports_no_available_cognitive_capabilities():
    router = CognitiveCapabilityRouter()

    assert router.available_capabilities() == ()
