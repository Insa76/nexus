from unittest.mock import MagicMock

from documents import (
    DocumentCapability,
    DocumentCognitiveAccess,
)
from engine.engine import Engine


def test_engine_exposes_document_cognitive_access():
    capability = MagicMock(spec=DocumentCapability)
    cognitive_access = DocumentCognitiveAccess(capability)

    runtime = MagicMock()
    runtime.tool_registry = MagicMock()
    runtime.tool_registry.resolve = MagicMock()

    engine = Engine(
        runtime=runtime,
        intent_provider=MagicMock(),
        document_capability=capability,
        document_cognitive_access=cognitive_access,
    )

    assert engine.document_cognitive_access is cognitive_access
    assert (
        engine.document_cognitive_access._capability
        is capability
    )
