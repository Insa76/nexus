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

    router.select.return_value = invocation
    router.invoke.return_value = result

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

    assert result["operation"] == "find_relevant"
    assert result["metadata"]["count"] == 0
