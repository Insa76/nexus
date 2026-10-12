from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_passes_cognitive_evidence_to_decision():
    runtime = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.execute = AsyncMock()

    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        return_value=Intent(
            action="documents.find_relevant",
            confidence=1.0,
            parameters={},
            original_text="busca documentos",
        ),
    )

    router = MagicMock()

    invocation = MagicMock()
    invocation.capability = "documents"
    invocation.operation = "find_relevant"
    invocation.parameters = {}

    cognitive_result = MagicMock()

    cognitive_summary = {
        "operation": "documents.find_relevant",
        "document_count": 2,
        "query_count": 2,
        "has_results": True,
        "status": "found",
        "result_count": 2,
    }

    router.available_operations.return_value = ()
    router.select.return_value = invocation
    router.invoke.return_value = cognitive_result
    router.summarize_operation_result.return_value = cognitive_summary

    engine = Engine(
        runtime=runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
    )

    decision = MagicMock()
    decision.decision_id = "decision-evidence"
    decision.selected_action = None
    decision.confidence = 0.0
    decision.reason = "evidencia cognitiva disponible"
    decision.requires_execution = False
    decision.alternatives = []
    decision.metadata = {}
    decision.is_executable = False

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    await engine.execute("busca documentos")

    decision_context = (
        engine.decision_engine.decide.call_args.kwargs["context"]
    )

    assert decision_context["cognitive_evidence"] == {
        "operation": "documents.find_relevant",
        "status": "found",
        "has_results": True,
        "result_count": 2,
    }
