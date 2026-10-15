from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_invokes_selected_cognitive_capability():
    runtime = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.tool_registry.resolve = MagicMock()

    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        return_value=Intent(
            action="documents.find_relevant",
            confidence=1.0,
            parameters={
                "name": "manual.pdf",
            },
            original_text="busca el manual",
        ),
    )

    router = MagicMock()

    invocation = MagicMock()
    invocation.capability = "documents"
    invocation.operation = "find_relevant"
    invocation.parameters = {
        "name": "manual.pdf",
    }

    result = {
        "operation": "find_relevant",
        "documents": [],
        "metadata": {
            "count": 0,
        },
    }

    summary = {
        "operation": "documents.find_relevant",
        "result_count": 0,
        "document_count": 0,
        "query_count": 0,
        "has_results": False,
        "status": "empty",
    }

    router.select.return_value = invocation
    router.invoke.return_value = result
    router.summarize_operation_result.return_value = summary

    engine = Engine(
        runtime=runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
    )

    decision = MagicMock()
    decision.decision_id = "decision-test"
    decision.selected_action = None
    decision.confidence = 0.0
    decision.reason = "capability cognitiva"
    decision.requires_execution = False
    decision.alternatives = []
    decision.metadata = {}
    decision.is_executable = False

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    await engine.execute("busca el manual")

    router.select.assert_called_once_with(
        action="documents.find_relevant",
        parameters={
            "name": "manual.pdf",
        },
    )

    router.invoke.assert_called_once()

    invoke_args = router.invoke.call_args

    assert invoke_args.args[0] is invocation
    assert invoke_args.kwargs["context"] is not None
    assert isinstance(
        invoke_args.kwargs["context"],
        dict,
    )

    router.summarize_operation_result.assert_called_once_with(
        result=result,
        operation="find_relevant",
    )

    decision_context = (
        engine.decision_engine.decide.call_args.kwargs["context"]
    )

    assert decision_context["cognitive_capability_result"] is result
    assert decision_context["cognitive_capability_summary"] == summary

    assert decision_context["cognitive_evidence"] == {
        "operation": "documents.find_relevant",
        "status": "empty",
        "has_results": False,
        "result_count": 0,
    }

    assert result["operation"] == "find_relevant"
    assert result["metadata"]["count"] == 0