from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_passes_cognitive_capability_result_to_decision():
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

    cognitive_result = MagicMock()

    router.select.return_value = invocation
    router.invoke.return_value = cognitive_result

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

    decision_context = (
        engine.decision_engine.decide.call_args.kwargs["context"]
    )

    assert (
        decision_context["cognitive_capability_result"]
        is cognitive_result
    )
