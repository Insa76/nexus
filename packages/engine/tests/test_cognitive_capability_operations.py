from unittest.mock import MagicMock

from documents import DocumentCognitiveAccess
from engine.cognitive_capabilities import (
    CognitiveCapabilityOperation,
    CognitiveCapabilityRouter,
)


def test_router_reports_available_cognitive_operations():
    access = MagicMock(spec=DocumentCognitiveAccess)

    router = CognitiveCapabilityRouter(
        document_access=access,
    )

    operations = router.available_operations()

    assert operations == (
        CognitiveCapabilityOperation(
            capability="documents",
            operation="find_relevant",
            action="documents.find_relevant",
        ),
    )


def test_router_reports_no_available_cognitive_operations():
    router = CognitiveCapabilityRouter()

    assert router.available_operations() == ()
