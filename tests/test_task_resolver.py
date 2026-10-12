from context import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)

from tasks import Task, TaskResolver, TaskStore


def test_resolver_returns_user_tasks() -> None:
    user = UserProfile.create(
        name="Diego",
    )

    context = AssistantContext(
        user=user,
    )

    matching = Task.create(
        title="Tarea del usuario",
        user_id=user.id,
    )

    unrelated = Task.create(
        title="Tarea de otro usuario",
        user_id="other-user",
    )

    store = TaskStore()
    store.add(matching)
    store.add(unrelated)

    resolver = TaskResolver(store)

    assert resolver.resolve(context) == [matching]


def test_resolver_returns_organization_tasks() -> None:
    organization = OrganizationProfile.create(
        name="Paraná Agency",
    )

    context = AssistantContext(
        organization=organization,
    )

    matching = Task.create(
        title="Tarea de la organización",
        organization_id=organization.id,
    )

    unrelated = Task.create(
        title="Tarea de otra organización",
        organization_id="other-organization",
    )

    store = TaskStore()
    store.add(matching)
    store.add(unrelated)

    resolver = TaskResolver(store)

    assert resolver.resolve(context) == [matching]


def test_resolver_returns_project_tasks() -> None:
    organization = OrganizationProfile.create(
        name="Paraná Agency",
    )

    project = ProjectContext.create(
        name="ORBIT",
        organization_id=organization.id,
    )

    context = AssistantContext(
        organization=organization,
        projects=(project,),
    )

    matching = Task.create(
        title="Tarea de ORBIT",
        project_id=project.id,
    )

    unrelated = Task.create(
        title="Tarea de otro proyecto",
        project_id="other-project",
    )

    store = TaskStore()
    store.add(matching)
    store.add(unrelated)

    resolver = TaskResolver(store)

    assert resolver.resolve(context) == [matching]


def test_resolver_combines_user_organization_and_project_tasks() -> None:
    user = UserProfile.create(
        name="Diego",
    )

    organization = OrganizationProfile.create(
        name="Paraná Agency",
    )

    project = ProjectContext.create(
        name="ORBIT",
        organization_id=organization.id,
    )

    context = AssistantContext(
        user=user,
        organization=organization,
        projects=(project,),
    )

    user_task = Task.create(
        title="Tarea personal",
        user_id=user.id,
    )

    organization_task = Task.create(
        title="Tarea de agencia",
        organization_id=organization.id,
    )

    project_task = Task.create(
        title="Tarea de ORBIT",
        project_id=project.id,
    )

    unrelated = Task.create(
        title="Tarea externa",
        user_id="other-user",
        organization_id="other-organization",
        project_id="other-project",
    )

    store = TaskStore()

    for task in (
        user_task,
        organization_task,
        project_task,
        unrelated,
    ):
        store.add(task)

    resolver = TaskResolver(store)

    assert resolver.resolve(context) == [
        user_task,
        organization_task,
        project_task,
    ]


def test_resolver_returns_empty_for_empty_context() -> None:
    context = AssistantContext()

    store = TaskStore()
    store.add(Task.create(title="Tarea sin contexto"))

    resolver = TaskResolver(store)

    assert resolver.resolve(context) == []


def test_resolver_does_not_mutate_store() -> None:
    user = UserProfile.create(
        name="Diego",
    )

    context = AssistantContext(
        user=user,
    )

    task = Task.create(
        title="Tarea",
        user_id=user.id,
    )

    store = TaskStore()
    store.add(task)

    resolver = TaskResolver(store)

    resolved = resolver.resolve(context)

    assert resolved == [task]
    assert store.list() == [task]
    assert store.count() == 1
