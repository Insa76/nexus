from context import AssistantContext
from processes.capability import ProcessCapability
from processes.cognitive import ProcessCognitiveAccess
from processes.models import Process
from processes.resolver import ProcessResolver
from processes.store import ProcessStore


class User:
    def __init__(self, user_id: str):
        self.id = user_id


def build_access() -> ProcessCognitiveAccess:
    store = ProcessStore()
    resolver = ProcessResolver(store)
    capability = ProcessCapability(
        store=store,
        resolver=resolver,
    )
    return ProcessCognitiveAccess(capability)


def test_cognitive_access_can_find_process_by_id():
    access = build_access()

    process = access._capability.create(
        name="Proceso de prueba",
        user_id="user-1",
    )

    result = access.get(process.id)

    assert result == process


def test_cognitive_access_can_list_processes():
    access = build_access()

    first = access._capability.create(
        name="Proceso 1",
        user_id="user-1",
    )
    second = access._capability.create(
        name="Proceso 2",
        user_id="user-1",
    )

    result = access.list()

    assert result == (first, second)


def test_cognitive_access_can_resolve_relevant_processes():
    access = build_access()

    process = access._capability.create(
        name="Proceso relevante",
        user_id="user-1",
    )

    context = AssistantContext(
        user=User("user-1"),
        organization=None,
        projects=[],
    )

    result = access.find_relevant(context=context)

    assert result.processes == (process,)
    assert result.metadata["operation"] == "processes.find_relevant"
    assert result.metadata["count"] == 1
