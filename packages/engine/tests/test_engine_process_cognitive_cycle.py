from unittest.mock import AsyncMock, MagicMock

import pytest

from context import AssistantContext

from engine.engine import Engine
from processes import ProcessCognitiveAccess
from runtime.execution_result import ExecutionResult


@pytest.mark.asyncio
async def test_engine_executes_process_cognitive_capability():
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

    process_access = MagicMock(
        spec=ProcessCognitiveAccess,
    )

    process_access.find_relevant.return_value = MagicMock(
        processes=(),
        metadata={
            "operation": "processes.find_relevant",
            "count": 0,
        },
    )

    router = MagicMock()

    invocation = MagicMock()
    invocation.capability = "processes"
    invocation.operation = "find_relevant"
    invocation.parameters = {}

    router.select.return_value = invocation
    router.invoke.return_value = process_access.find_relevant.return_value

    router.summarize_operation_result.return_value = {
        "operation": "processes.find_relevant",
        "document_count": 0,
        "query_count": 0,
        "has_results": False,
        "status": "empty",
        "result_count": 0,
    }

    intent_provider = MagicMock()

    intent = MagicMock()
    intent.action = "processes.find_relevant"
    intent.original_text = "buscá los procesos relevantes"
    intent.parameters = {}
    intent.confidence = 1.0
    intent.is_compound = False

    intent_provider.recognize = AsyncMock(
        return_value=intent,
    )

    engine = Engine(
        runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
        process_cognitive_access=process_access,
        assistant_context=AssistantContext(
            user=None,
            organization=None,
            projects=[],
        ),
    )

    result = await engine.execute(
        "buscá los procesos relevantes",
    )

    router.select.assert_called_once()
    router.invoke.assert_called_once()
    assert result is not None
