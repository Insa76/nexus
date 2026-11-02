
from types import SimpleNamespace

from context import AssistantContext
from processes.capability import ProcessCapability
from processes.cognitive import ProcessCognitiveAccess
from processes.models import Process
from processes.resolver import ProcessResolver
from processes.store import ProcessStore


def build_access() -> ProcessCognitiveAccess:
    store = ProcessStore()
    resolver = ProcessResolver(store)
    capability = ProcessCapability(
        store=store,
        resolver=resolver,
    )
    return ProcessCognitiveAccess(capability)


def make_context(user_id: str) -> AssistantContext:
    return AssistantContext(
        user=SimpleNamespace(id=user_id),
        organization=None,
        projects=(),
    )


def test_cognitive_access_can_find_process_by_id():
    access = build_access()

    process = access._capability.create(
        name="Proceso de prueba",
        user_id="user-1",
    )

    result = access.get(
        process.id,
        context=make_context("user-1"),
    )

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

    result = access.list(
        context=make_context("user-1"),
    )

    assert result == (first, second)


def test_cognitive_access_cannot_get_process_from_another_user():
    access = build_access()

    process = access._capability.create(
        name="Proceso ajeno",
        user_id="user-2",
    )

    result = access.get(
        process.id,
        context=make_context("user-1"),
    )

    assert result is None


def test_cognitive_access_lists_only_processes_from_current_context():
    access = build_access()

    own_process = access._capability.create(
        name="Proceso propio",
        user_id="user-1",
    )
    access._capability.create(
        name="Proceso ajeno",
        user_id="user-2",
    )

    result = access.list(
        context=make_context("user-1"),
    )

    assert result == (own_process,)
