
from unittest.mock import AsyncMock, MagicMock

import pytest

from context import AssistantContext, UserProfile
from engine.cognitive_capabilities import CognitiveCapabilityRouter
from engine.engine import Engine
from planner.intent import Intent
from rules.capability import RuleCapability
from rules.cognitive import RuleCognitiveAccess
from rules.resolver import RuleResolver
from rules.store import RuleStore
from runtime.execution_result import ExecutionResult


@pytest.mark.asyncio
async def test_engine_rule_capability_uses_assistant_context():
    store = RuleStore()
    resolver = RuleResolver(store)
    capability = RuleCapability(
        store=store,
        resolver=resolver,
    )
    rule_access = RuleCognitiveAccess(capability)

    router = CognitiveCapabilityRouter(
        rule_access=rule_access,
    )

    rule = capability.create(
        name="Regla de integración",
        description="Regla asociada al usuario de la solicitud.",
        user_id="user-1",
    )

    assistant_context = AssistantContext(
        user=UserProfile(
            id="user-1",
            name="Usuario de prueba",
        ),
        organization=None,
        projects=(),
    )

    runtime = MagicMock()
    runtime.tool_registry.describe.return_value = []
    runtime.execute = AsyncMock(
        return_value=ExecutionResult(
            success=True,
            message="Ejecución de prueba completada.",
            output={},
            metadata={},
        ),
    )

    intent_provider = MagicMock()
    intent_provider.recognize = AsyncMock(
        return_value=Intent(
            action="rules.find_relevant",
            confidence=1.0,
            parameters={},
            original_text="buscá las reglas relevantes",
        ),
    )

    engine = Engine(
        runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
        rule_capability=capability,
        rule_cognitive_access=rule_access,
        assistant_context=assistant_context,
    )

    result = await engine.execute("buscá las reglas relevantes")

    assert result is not None

    memory_entries = engine._memory.recent(50)

    capability_result_entries = [
        entry
        for entry in memory_entries
        if entry.type == "cognitive_capability_result"
    ]

    assert capability_result_entries

    cognitive_result = capability_result_entries[-1].data["result"]

    assert cognitive_result.rules == (rule,)
    assert cognitive_result.metadata["count"] == 1
