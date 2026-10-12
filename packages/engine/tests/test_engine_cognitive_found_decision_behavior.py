from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent
from runtime.execution_result import ExecutionResult


@pytest.mark.asyncio
async def test_engine_can_continue_execution_after_found_cognitive_result():
    runtime = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.execute = AsyncMock(
    return_value=ExecutionResult(
        success=True,
        message="ok",
        output={},
        metadata={},
    ),
)

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
    decision.decision_id = "decision-found"
    decision.selected_action = "documents.find_relevant"
    decision.confidence = 1.0
    decision.reason = "Se encontraron documentos relevantes."
    decision.requires_execution = True
    decision.alternatives = []
    decision.metadata = {
        "status": "cognitive_found",
    }
    decision.is_executable = True

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    await engine.execute("busca el manual")

    decision_context = (
        engine.decision_engine.decide.call_args.kwargs["context"]
    )

    assert decision_context["cognitive_evidence"]["status"] == "found"
    assert decision.requires_execution is True
    assert decision.selected_action == "documents.find_relevant"

    runtime.execute.assert_awaited_once()
