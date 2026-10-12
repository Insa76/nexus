import pytest

from context import AssistantContext
from processes.capability import ProcessCapability
from processes.cognitive import ProcessCognitiveAccess
from processes.resolver import ProcessResolver
from processes.store import ProcessStore


class User:
    def __init__(self, user_id: str):
        self.id = user_id


@pytest.mark.asyncio
async def test_engine_executes_real_process_cognitive_cycle():
    store = ProcessStore()
    resolver = ProcessResolver(store)
    capability = ProcessCapability(
        store=store,
        resolver=resolver,
    )
    cognitive_access = ProcessCognitiveAccess(capability)

    process = capability.create(
        name="Proceso de prueba",
        description="Proceso relevante para el contexto actual.",
        user_id="user-1",
    )

    context = AssistantContext(
        user=User("user-1"),
        organization=None,
        projects=[],
    )

    result = cognitive_access.find_relevant(context=context)

    assert result.processes == (process,)
    assert result.metadata["operation"] == "processes.find_relevant"
    assert result.metadata["count"] == 1
