from context import AssistantContext

from processes import (
    Process,
    ProcessStatus,
    ProcessResolver,
    ProcessStore,
    ProcessCognitiveAccess,
    ProcessCognitiveResult,
    ProcessCapability,
)


def test_process_create():
    process = Process.create(
        name="Proceso de ventas",
        description="Seguimiento comercial",
    )

    assert process.id
    assert process.name == "Proceso de ventas"
    assert process.description == "Seguimiento comercial"
    assert process.status == ProcessStatus.PENDING


def test_process_store():
    store = ProcessStore()

    process = Process.create(
        name="Proceso de ventas",
    )

    store.add(process)

    assert store.get(process.id) == process
    assert store.list() == [process]
    assert store.count() == 1

    updated = Process(
        id=process.id,
        name=process.name,
        description=process.description,
        status=ProcessStatus.IN_PROGRESS,
        user_id=process.user_id,
        organization_id=process.organization_id,
        project_id=process.project_id,
        created_at=process.created_at,
    )

    store.update(updated)

    assert store.get(process.id).status == ProcessStatus.IN_PROGRESS

    removed = store.remove(process.id)

    assert removed == updated
    assert store.count() == 0


def test_process_resolver_by_user():
    store = ProcessStore()

    process = Process.create(
        name="Proceso personal",
        user_id="user-1",
    )

    store.add(process)

    context = AssistantContext(
        user=type("User", (), {"id": "user-1"})(),
        organization=None,
        projects=[],
    )

    resolver = ProcessResolver(store)

    resolved = resolver.resolve(context)

    assert resolved == [process]


def test_process_capability():
    store = ProcessStore()
    resolver = ProcessResolver(store)

    capability = ProcessCapability(
        store=store,
        resolver=resolver,
    )

    process = capability.create(
        name="Proceso operativo",
        description="Proceso creado mediante capability",
    )

    assert process.name == "Proceso operativo"
    assert capability.get(process.id) == process
    assert capability.list() == [process]

    removed = capability.remove(process.id)

    assert removed == process
    assert capability.list() == []

def test_process_cognitive_access():
    store = ProcessStore()
    resolver = ProcessResolver(store)

    capability = ProcessCapability(
        store=store,
        resolver=resolver,
    )

    process = capability.create(
        name="Proceso contextual",
        user_id="user-1",
    )

    access = ProcessCognitiveAccess(capability)

    context = AssistantContext(
        user=type("User", (), {"id": "user-1"})(),
        organization=None,
        projects=[],
    )

    result = access.find_relevant(
        context=context,
    )

    assert result.processes == (process,)
    assert result.metadata["operation"] == "processes.find_relevant"
    assert result.metadata["count"] == 1
