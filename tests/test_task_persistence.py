from datetime import datetime, timezone

from context import AssistantContext, OrganizationProfile, ProjectContext, UserProfile
from tasks import Task, TaskCapability, TaskResolver, TaskStatus, TaskStore


def _context() -> AssistantContext:
    organization = OrganizationProfile.create("Org")
    user = UserProfile.create("User", organization_id=organization.id)
    project = ProjectContext.create("Project", organization.id)
    return AssistantContext(
        user=user,
        organization=organization,
        projects=(project,),
        metadata={"active_project_id": project.id},
    )


def test_sqlite_task_store_restores_tasks_after_reopen(tmp_path):
    db_path = tmp_path / "tasks.sqlite3"
    due_at = datetime(2026, 11, 10, 12, tzinfo=timezone.utc)
    original = Task.create(
        "Persist me",
        description="Details",
        priority="high",
        user_id="user-1",
        organization_id="org-1",
        project_id="project-1",
        due_at=due_at,
    )

    first_store = TaskStore(db_path=db_path)
    first_store.add(original)

    reopened_store = TaskStore(db_path=db_path)
    restored = reopened_store.get(original.id)

    assert restored == original
    assert reopened_store.list() == [original]
    assert restored is not None and restored.due_at == due_at


def test_context_creation_derives_scope_ids_from_active_context(tmp_path):
    context = _context()
    store = TaskStore(db_path=tmp_path / "tasks.sqlite3")
    capability = TaskCapability(store, TaskResolver(store))

    task = capability.create_for_context(
        title="Prepare release",
        context=context,
        description="Release checklist",
        priority="high",
    )

    assert task.user_id == context.user.id
    assert task.organization_id == context.organization.id
    assert task.project_id == context.projects[0].id
    assert capability.get(task.id, context=context) == task


def test_task_transition_is_persisted_and_scope_checked(tmp_path):
    context = _context()
    store = TaskStore(db_path=tmp_path / "tasks.sqlite3")
    capability = TaskCapability(store, TaskResolver(store))
    task = capability.create_for_context(title="Finish feature", context=context)

    updated = capability.transition(
        task.id, TaskStatus.IN_PROGRESS, context=context
    )

    assert updated is not None
    assert updated.status is TaskStatus.IN_PROGRESS
    assert TaskStore(db_path=tmp_path / "tasks.sqlite3").get(task.id) == updated


def test_project_task_does_not_leak_through_user_scope(tmp_path):
    context = _context()
    other_project = ProjectContext.create(
        "Other project", context.organization.id
    )
    store = TaskStore(db_path=tmp_path / "tasks.sqlite3")
    store.add(Task.create(
        "Other project task",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=other_project.id,
    ))

    assert TaskResolver(store).resolve(context) == []
