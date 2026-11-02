from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_passes_empty_cognitive_result_to_decision():
    runtime = MagicMock()
    runtime.execute = AsyncMock()
    runtime.tool_registry.describe.return_value = []

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
        "document_count": 0,
        "query_count": 0,
        "has_results": False,
        "status": "empty",
        "result_count": 0,
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
    decision.decision_id = "decision-empty"
    decision.selected_action = None
    decision.confidence = 0.0
    decision.reason = "no se encontraron documentos"
    decision.requires_execution = False
    decision.alternatives = []
    decision.metadata = {}
    decision.is_executable = False

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    result = await engine.execute("busca documentos")

    assert result.success is True
    assert result.output["operation"] == "documents.find_relevant"
    assert result.output["status"] == "empty"
    assert result.output["documents"] == []
    assert "No encontré documentos" in result.metadata["response"]
    runtime.execute.assert_not_awaited()

    decision_context = (
        engine.decision_engine.decide.call_args.kwargs["context"]
    )

    assert (
        decision_context["cognitive_capability_summary"]
        == cognitive_summary
    )

    assert (
        decision_context["cognitive_capability_summary"]["status"]
        == "empty"
    )
