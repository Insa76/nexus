from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from engine.engine import Engine
from planner.intent import Intent


@pytest.mark.asyncio
async def test_engine_returns_found_documents_in_execution_result():
    runtime = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.tool_registry.resolve = MagicMock()

    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        return_value=Intent(
            action="documents.find_relevant",
            confidence=1.0,
            parameters={"name": "manual.pdf"},
            original_text="busca el manual",
        ),
    )

    document = SimpleNamespace(
        name="manual.pdf",
        mime_type="application/pdf",
        description="Manual de diagnóstico",
        source="diagnostic://manual",
    )

    query_result = SimpleNamespace(
        total=1,
        offset=0,
        limit=None,
        has_more=False,
    )

    cognitive_result = SimpleNamespace(
        query=query_result,
        documents=(document,),
    )

    cognitive_summary = {
        "operation": "documents.find_relevant",
        "status": "found",
        "has_results": True,
        "result_count": 1,
    }

    router = MagicMock()
    invocation = SimpleNamespace(
        capability="documents",
        operation="find_relevant",
        parameters={"name": "manual.pdf"},
    )

    router.available_operations.return_value = ()
    router.select.return_value = invocation
    router.invoke.return_value = cognitive_result
    router.summarize_operation_result.return_value = (
        cognitive_summary
    )

    engine = Engine(
        runtime=runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
    )

    decision = MagicMock()
    decision.decision_id = "decision-document-test"
    decision.selected_action = "documents.find_relevant"
    decision.confidence = 1.0
    decision.reason = "Consulta documental"
    decision.requires_execution = True
    decision.alternatives = []
    decision.metadata = {}
    decision.is_executable = True

    engine.decision_engine.decide = MagicMock(
        return_value=decision,
    )

    result = await engine.execute("busca el manual")

    assert result.success is True
    assert result.output["operation"] == "documents.find_relevant"
    assert result.output["status"] == "found"
    assert result.output["total"] == 1
    assert result.output["documents"] == [
        {
            "name": "manual.pdf",
            "mime_type": "application/pdf",
            "description": "Manual de diagnóstico",
            "source": "diagnostic://manual",
        }
    ]

    assert result.metadata["response"]
    router.invoke.assert_called_once()
    runtime.execute.assert_not_called()