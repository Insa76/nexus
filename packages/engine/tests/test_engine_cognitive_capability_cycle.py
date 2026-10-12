from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_selects_cognitive_capability_without_executing_it():
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
    router.select.return_value = MagicMock(
        capability="documents",
        operation="find_relevant",
        parameters={
            "name": "manual.pdf",
        },
    )

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

    result = await engine.execute("busca el manual")

    router.select.assert_called_once_with(
        action="documents.find_relevant",
        parameters={
            "name": "manual.pdf",
        },
    )

    engine.decision_engine.decide.assert_called_once()

    assert any(
    entry.type == "cognitive_capability"
    for entry in engine.memory._entries
    )
    assert result.success is False
