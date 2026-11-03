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
