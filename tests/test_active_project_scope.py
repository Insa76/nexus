from context import (
    AssistantContext,
    OrganizationProfile,
    ProjectContext,
    UserProfile,
)
from documents import build_document_services
from documents.context_resolver import DocumentContextResolver
from processes import Process, ProcessResolver, ProcessStore
from rules import Rule, RuleResolver, RuleStore
from tasks import Task, TaskResolver, TaskStore


def _workspace_context(active_project_id: str | None) -> AssistantContext:
    organization = OrganizationProfile.create("Organización")
    user = UserProfile.create(
        "Usuario",
        organization_id=organization.id,
    )
    project_a = ProjectContext.create(
        "Proyecto A",
        organization.id,
    )
    project_b = ProjectContext.create(
        "Proyecto B",
        organization.id,
    )
    resolved_active_project_id = {
        "project-a": project_a.id,
        "project-b": project_b.id,
    }.get(active_project_id)
    return AssistantContext(
        user=user,
        organization=organization,
        projects=(project_a, project_b),
        metadata={"active_project_id": resolved_active_project_id},
    )


def test_task_resolver_limits_project_tasks_to_active_project():
    context = _workspace_context("project-a")
    project_a, project_b = context.projects
    task_a = Task.create("Tarea A", project_id=project_a.id)
    task_b = Task.create("Tarea B", project_id=project_b.id)
    org_task = Task.create(
        "Tarea organización",
        organization_id=context.organization.id,
    )
    store = TaskStore()
    for task in (task_a, task_b, org_task):
        store.add(task)

    result = TaskResolver(store).resolve(context)

    assert result == [task_a, org_task]


def test_process_resolver_limits_project_processes_to_active_project():
    context = _workspace_context("project-a")
    project_a, project_b = context.projects
    process_a = Process.create("Proceso A", project_id=project_a.id)
    process_b = Process.create("Proceso B", project_id=project_b.id)
    org_process = Process.create(
        "Proceso organización",
        organization_id=context.organization.id,
    )
    store = ProcessStore()
    for process in (process_a, process_b, org_process):
        store.add(process)

    result = ProcessResolver(store).resolve(context)

    assert result == [process_a, org_process]


def test_rule_resolver_limits_project_rules_to_active_project():
    context = _workspace_context("project-a")
    project_a, project_b = context.projects
    rule_a = Rule.create("Regla A", project_id=project_a.id)
    rule_b = Rule.create("Regla B", project_id=project_b.id)
    org_rule = Rule.create(
        "Regla organización",
        organization_id=context.organization.id,
    )
    store = RuleStore()
    for rule in (rule_a, rule_b, org_rule):
        store.add(rule)

    result = RuleResolver(store).resolve(context)

    assert result == [rule_a, org_rule]


def test_document_resolver_limits_project_documents_to_active_project():
    context = _workspace_context("project-a")
    project_a, project_b = context.projects
    services = build_document_services()
    document_a = services.access.create_document(
        name="Documento A",
        mime_type="text/plain",
        source="a.txt",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=project_a.id,
    )
    document_b = services.access.create_document(
        name="Documento B",
        mime_type="text/plain",
        source="b.txt",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=project_b.id,
    )

    result = DocumentContextResolver(
        services.access,
    ).resolve_from_context(context)

    assert result.documents == (document_a,)
    assert result.selection.project_ids == (project_a.id,)
    assert document_b not in tuple(match.document for match in result.matches)


def test_explicitly_unselected_project_hides_project_scoped_resources():
    context = _workspace_context(None)
    project_a = context.projects[0]
    task = Task.create("Tarea A", project_id=project_a.id)
    store = TaskStore()
    store.add(task)

    assert TaskResolver(store).resolve(context) == []


def test_legacy_context_without_active_project_metadata_keeps_all_projects():
    context = _workspace_context(None)
    context = AssistantContext(
        user=context.user,
        organization=context.organization,
        projects=context.projects,
        metadata={},
    )
    project_a, project_b = context.projects
    task_a = Task.create("Tarea A", project_id=project_a.id)
    task_b = Task.create("Tarea B", project_id=project_b.id)
    store = TaskStore()
    store.add(task_a)
    store.add(task_b)

    assert TaskResolver(store).resolve(context) == [task_a, task_b]



def test_process_and_rule_project_records_do_not_leak_through_user_or_org_scope():
    context = _workspace_context("project-a")
    project_a, project_b = context.projects

    process_other_project = Process.create(
        "Proceso privado de B",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=project_b.id,
    )
    process_active_project = Process.create(
        "Proceso de A",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=project_a.id,
    )
    rule_other_project = Rule.create(
        "Regla privada de B",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=project_b.id,
    )
    rule_active_project = Rule.create(
        "Regla de A",
        user_id=context.user.id,
        organization_id=context.organization.id,
        project_id=project_a.id,
    )

    process_store = ProcessStore()
    process_store.add(process_other_project)
    process_store.add(process_active_project)
    rule_store = RuleStore()
    rule_store.add(rule_other_project)
    rule_store.add(rule_active_project)

    assert ProcessResolver(process_store).resolve(context) == [process_active_project]
    assert RuleResolver(rule_store).resolve(context) == [rule_active_project]
