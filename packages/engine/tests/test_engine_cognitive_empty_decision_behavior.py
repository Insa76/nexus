from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_can_block_execution_after_empty_cognitive_result():
    runtime = MagicMock()
    runtime.tool_registry.describe.return_value = []

    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        return_value=Intent(
            action="documents.find_relevant",
            confidence=1.0,
            parameters={},
            original_text="busca el manual",
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
    decision.reason = "No se encontraron documentos relevantes."
    decision.requires_execution = False
    decision.alternatives = []
    decision.metadata = {
        "status": "cognitive_empty",
    }
    decision.is_executable = False

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    await engine.execute("busca el manual")

    decision_context = (
        engine.decision_engine.decide.call_args.kwargs["context"]
    )

    assert decision_context["cognitive_evidence"]["status"] == "empty"
    assert decision.requires_execution is False
    assert decision.selected_action is None

    runtime.execute.assert_not_called()
