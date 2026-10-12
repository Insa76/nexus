from unittest.mock import MagicMock

from documents import DocumentCapability
from documents.context_access import DocumentContextAccess

from engine.engine import Engine
from runtime.runtime import Runtime


def test_engine_exposes_document_capability():
    context_access = MagicMock(
        spec=DocumentContextAccess,
    )

    capability = DocumentCapability(
        context_access=context_access,
    )

    runtime = MagicMock(
        spec=Runtime,
    )

    runtime.tool_registry = MagicMock()
    runtime.tool_registry.resolve = MagicMock()

    engine = Engine(
        runtime=runtime,
        intent_provider=MagicMock(),
        document_capability=capability,
    )

    assert engine.document_capability is capability
