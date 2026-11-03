import asyncio

from bootstrap.bootstrap import build_engine
from context import AssistantContext, OrganizationProfile, ProjectContext, UserProfile
from planner.intent import Intent
from tasks import TaskStore


class FixedIntentProvider:
    def __init__(self, action: str, parameters: dict):
        self.action = action
        self.parameters = parameters

    async def recognize(self, text, capabilities=None, context=None):
        return Intent(
            action=self.action,
            confidence=1.0,
            parameters=self.parameters,
            original_text=text,
        )


def _context():
    organization = OrganizationProfile.create("NEXUS Test Org")
    user = UserProfile.create("Test User", organization_id=organization.id)
    project = ProjectContext.create("NEXUS Test Project", organization.id)
    return AssistantContext(
        user=user,
        organization=organization,
        projects=(project,),
        metadata={"active_project_id": project.id},
    )


def _build_test_engine(monkeypatch, tmp_path):
    monkeypatch.setenv("NEXUS_TASKS_DB_PATH", str(tmp_path / "tasks.sqlite3"))
    monkeypatch.setenv("NEXUS_SECURITY_DB_PATH", str(tmp_path / "security.sqlite3"))
    monkeypatch.setenv("NEXUS_SEMANTIC_MEMORY_DB_PATH", str(tmp_path / "semantic.sqlite3"))
    engine = build_engine(assistant_context=_context())
    engine._intent_provider = FixedIntentProvider(
        "tasks.create",
        {"title": "Prepare V1 release", "priority": "high"},
    )
    return engine


def test_task_mutation_waits_for_explicit_confirmation(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)
    db_path = tmp_path / "tasks.sqlite3"

    proposal = asyncio.run(engine.execute("Crear tarea para preparar V1"))

    assert proposal.success is True
    assert proposal.metadata["confirmation_required"] is True
    assert TaskStore(db_path=db_path).list() == []

    confirmed = engine.confirm_task_operation(
        proposal.metadata["confirmation_token"],
        approved=True,
    )

    assert confirmed.success is True
    tasks = TaskStore(db_path=db_path).list()
    assert len(tasks) == 1
    assert tasks[0].title == "Prepare V1 release"
    assert tasks[0].project_id == engine.assistant_context.projects[0].id


def test_rejected_task_proposal_does_not_write(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)
    db_path = tmp_path / "tasks.sqlite3"

    proposal = asyncio.run(engine.execute("Crear tarea"))

    rejected = engine.confirm_task_operation(
        proposal.metadata["confirmation_token"],
        approved=False,
    )

    assert rejected.success is True
    assert rejected.output["status"] == "cancelled"
    assert TaskStore(db_path=db_path).list() == []


def test_task_proposal_is_invalidated_when_active_context_changes(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)
    db_path = tmp_path / "tasks.sqlite3"

    proposal = asyncio.run(engine.execute("Crear tarea"))
    other_context = _context()
    engine.set_assistant_context(other_context)

    result = engine.confirm_task_operation(
        proposal.metadata["confirmation_token"],
        approved=True,
    )

    assert result.success is False
    assert result.output["status"] == "scope_changed"
    assert TaskStore(db_path=db_path).list() == []


def test_task_mutation_requires_security_authorization(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)
    engine._task_action_authorizer = lambda action: False
    db_path = tmp_path / "tasks.sqlite3"

    proposal = asyncio.run(engine.execute("Crear tarea"))
    result = engine.confirm_task_operation(
        proposal.metadata["confirmation_token"],
        approved=True,
    )

    assert result.success is False
    assert result.output["status"] == "unauthorized"
    assert TaskStore(db_path=db_path).list() == []



def test_invalid_task_proposal_does_not_issue_or_store_confirmation(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)
    engine._intent_provider = FixedIntentProvider(
        "tasks.create",
        {"title": "   ", "priority": "normal"},
    )

    result = asyncio.run(engine.execute("Crear tarea sin título"))

    assert result.success is False
    assert result.output["status"] == "invalid_parameters"
    assert result.metadata.get("confirmation_token") is None
    assert engine._pending_task_operations == {}


def test_confirmation_token_is_single_use(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)

    proposal = asyncio.run(engine.execute("Crear tarea"))
    token = proposal.metadata["confirmation_token"]

    first = engine.confirm_task_operation(token, approved=True)
    second = engine.confirm_task_operation(token, approved=True)

    assert first.success is True
    assert second.success is False
    assert second.output["status"] == "not_found"
    assert len(TaskStore(db_path=tmp_path / "tasks.sqlite3").list()) == 1


def test_update_proposal_binds_the_resolved_task_id(monkeypatch, tmp_path):
    engine = _build_test_engine(monkeypatch, tmp_path)
    context = engine.assistant_context
    access = engine.cognitive_capability_router._task_access
    task = access.create(context=context, title="Original task")
    engine._intent_provider = FixedIntentProvider(
        "tasks.update",
        {"task_reference": "Original task", "priority": "urgent"},
    )

    proposal = asyncio.run(engine.execute("Cambiar prioridad de Original task"))
    pending = engine._pending_task_operations[proposal.metadata["confirmation_token"]]

    assert pending["parameters"]["task_id"] == task.id
    assert "task_reference" not in pending["parameters"]

    confirmed = engine.confirm_task_operation(
        proposal.metadata["confirmation_token"],
        approved=True,
    )

    assert confirmed.success is True
    restored = TaskStore(db_path=tmp_path / "tasks.sqlite3").get(task.id)
    assert restored is not None
    assert restored.priority == "urgent"
