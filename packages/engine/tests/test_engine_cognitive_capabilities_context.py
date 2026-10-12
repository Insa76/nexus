from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent
from runtime.execution_result import ExecutionResult


@pytest.mark.asyncio
async def test_engine_exposes_cognitive_operations_to_decision():
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
            original_text="busca documentos",
        ),
    )

    router = MagicMock()

    operation = MagicMock()
    operation.action = "documents.find_relevant"
    operation.capability = "documents"
    operation.operation = "find_relevant"

    router.available_operations.return_value = (operation,)
    router.select.return_value = None

    engine = Engine(
        runtime=runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
    )

    decision = MagicMock()
    decision.decision_id = "decision-test"
    decision.selected_action = "documents.find_relevant"
    decision.confidence = 1.0
    decision.reason = "capability disponible"
    decision.requires_execution = True
    decision.alternatives = []
    decision.metadata = {}
    decision.is_executable = True

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    await engine.execute("busca documentos")

    capabilities = (
        engine.decision_engine.decide.call_args.kwargs["capabilities"]
    )

    assert {
        "action": "documents.find_relevant",
        "capability": "documents",
        "operation": "find_relevant",
        "type": "cognitive",
    } in capabilities
