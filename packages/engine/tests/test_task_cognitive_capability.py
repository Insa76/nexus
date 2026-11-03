from context import AssistantContext, OrganizationProfile, ProjectContext
from engine.cognitive_capabilities import CognitiveCapabilityRouter
from tasks import (
    Task,
    TaskCapability,
    TaskCognitiveAccess,
    TaskResolver,
    TaskStore,
)


def _task_access():
    store = TaskStore()
    resolver = TaskResolver(store)
    capability = TaskCapability(store=store, resolver=resolver)
    return store, TaskCognitiveAccess(capability)


def test_task_operations_are_registered_in_cognitive_router():
    _, access = _task_access()
    router = CognitiveCapabilityRouter(task_access=access)

    actions = {item.action for item in router.descriptors}

    assert {
        "tasks.find_relevant",
        "tasks.get",
        "tasks.list",
    }.issubset(actions)


def test_task_router_uses_active_project_context():
    store, access = _task_access()
    organization = OrganizationProfile.create("Organización")
    project_a = ProjectContext.create("Proyecto A", organization.id)
    project_b = ProjectContext.create("Proyecto B", organization.id)
    context = AssistantContext(
        organization=organization,
        projects=(project_a, project_b),
        metadata={"active_project_id": project_a.id},
    )
    task_a = Task.create("Tarea A", project_id=project_a.id)
    task_b = Task.create("Tarea B", project_id=project_b.id)
    store.add(task_a)
    store.add(task_b)

    router = CognitiveCapabilityRouter(task_access=access)
    invocation = router.select(action="tasks.find_relevant")
    assert invocation is not None

    result = router.invoke(
        invocation,
        context={},
        assistant_context=context,
    )

    assert result.tasks == (task_a,)
    assert router.summarize_operation_result(
        result,
        operation="tasks.find_relevant",
    )["result_count"] == 1


def test_bootstrap_exposes_tasks_through_runtime_router():
    from bootstrap.bootstrap import build_engine

    engine = build_engine()
    router = engine.cognitive_capability_router

    assert router is not None
    actions = {item.action for item in router.descriptors}
    assert "tasks.find_relevant" in actions
