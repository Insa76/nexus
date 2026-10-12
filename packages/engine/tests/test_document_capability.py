from unittest.mock import MagicMock

from documents import DocumentCapability
from engine.engine import Engine


def test_engine_exposes_document_capability():
    capability = DocumentCapability(
        context_access=None,
    )

    runtime = MagicMock()
    runtime.tool_registry = MagicMock()
    runtime.tool_registry.resolve = MagicMock()

    engine = Engine(
        runtime=runtime,
        intent_provider=MagicMock(),
        document_capability=capability,
    )

    assert engine.document_capability is capability
