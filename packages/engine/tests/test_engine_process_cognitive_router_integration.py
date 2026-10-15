
from unittest.mock import AsyncMock, MagicMock

import pytest

from context import AssistantContext, UserProfile
from engine.cognitive_capabilities import CognitiveCapabilityRouter
from engine.engine import Engine
from planner.intent import Intent
from processes.capability import ProcessCapability
from processes.cognitive import ProcessCognitiveAccess
from processes.resolver import ProcessResolver
from processes.store import ProcessStore
from runtime.execution_result import ExecutionResult



@pytest.mark.asyncio
async def test_engine_process_capability_uses_assistant_context():
    store = ProcessStore()
    resolver = ProcessResolver(store)
    capability = ProcessCapability(
        store=store,
        resolver=resolver,
    )
    process_access = ProcessCognitiveAccess(capability)
    router = CognitiveCapabilityRouter(
        process_access=process_access,
    )

    process = capability.create(
        name="Proceso de integración",
        description="Proceso asociado al usuario de la solicitud.",
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
            action="processes.find_relevant",
            confidence=1.0,
            parameters={},
            original_text="buscá los procesos relevantes",
        ),
    )

    engine = Engine(
        runtime,
        intent_provider=intent_provider,
        cognitive_capability_router=router,
        process_capability=capability,
        process_cognitive_access=process_access,
        assistant_context=assistant_context,
    )


    result = await engine.execute(
        "buscá los procesos relevantes"
    )

    assert result is not None

    memory_entries = engine._memory.recent(50)

    capability_result_entries = [
        entry
        for entry in memory_entries
            if entry.type == "cognitive_capability_result"
    ]

    assert capability_result_entries

    cognitive_result = capability_result_entries[-1].data["result"]

    assert cognitive_result.processes == (process,)
    assert cognitive_result.metadata["count"] == 1
