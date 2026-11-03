import asyncio

from bootstrap.bootstrap import build_engine
from context import AssistantContext, OrganizationProfile, ProjectContext, UserProfile
from planner.intent import Intent
from rules.models import RuleStatus


class FixedIntentProvider:
    def __init__(self, action, parameters):
        self.action = action
        self.parameters = parameters

    async def recognize(self, text, capabilities=None, context=None):
        return Intent(action=self.action, confidence=1.0, parameters=self.parameters, original_text=text)


def build_test_engine(monkeypatch, tmp_path, action, parameters):
    for key, filename in (
        ("NEXUS_TASKS_DB_PATH", "tasks.sqlite3"),
        ("NEXUS_PROCESSES_DB_PATH", "processes.sqlite3"),
        ("NEXUS_RULES_DB_PATH", "rules.sqlite3"),
        ("NEXUS_SECURITY_DB_PATH", "security.sqlite3"),
        ("NEXUS_SEMANTIC_MEMORY_DB_PATH", "semantic.sqlite3"),
    ):
        monkeypatch.setenv(key, str(tmp_path / filename))
    organization = OrganizationProfile.create("Mutation Test Org")
    user = UserProfile.create("Mutation Test User", organization_id=organization.id)
    project = ProjectContext.create("Mutation Test Project", organization.id)
    context = AssistantContext(
        user=user, organization=organization, projects=(project,),
        metadata={"active_project_id": project.id},
    )
    engine = build_engine(assistant_context=context)
    engine._intent_provider = FixedIntentProvider(action, parameters)
    return engine


def test_process_create_is_not_written_before_confirmation(monkeypatch, tmp_path):
    engine = build_test_engine(monkeypatch, tmp_path, "processes.create", {"name": "Onboarding"})
    proposal = asyncio.run(engine.execute("Crear proceso de onboarding"))
    assert proposal.metadata["confirmation_required"] is True
    assert engine.process_capability.store.count() == 0
    confirmed = engine.confirm_task_operation(proposal.metadata["confirmation_token"], approved=True)
    assert confirmed.success is True
    process = engine.process_capability.store.list()[0]
    assert process.name == "Onboarding"
    assert process.project_id == engine.assistant_context.projects[0].id


def test_rule_create_and_deactivate_require_confirmation(monkeypatch, tmp_path):
    engine = build_test_engine(monkeypatch, tmp_path, "rules.create", {"name": "Aprobación previa"})
    proposal = asyncio.run(engine.execute("Crear regla"))
    assert proposal.metadata["confirmation_required"] is True
    assert engine.rule_capability.store.count() == 0
    created = engine.confirm_task_operation(proposal.metadata["confirmation_token"], approved=True)
    assert created.success is True
    rule = engine.rule_capability.store.list()[0]
    assert rule.status == RuleStatus.ACTIVE

    engine._intent_provider = FixedIntentProvider(
        "rules.set_status", {"rule_reference": rule.name, "target_status": "inactive"},
    )
    status_proposal = asyncio.run(engine.execute("Desactivar regla"))
    assert status_proposal.metadata["confirmation_required"] is True
    changed = engine.confirm_task_operation(status_proposal.metadata["confirmation_token"], approved=True)
    assert changed.success is True
    assert engine.rule_capability.store.get(rule.id).status == RuleStatus.INACTIVE


def test_rejected_process_rule_proposal_does_not_write(monkeypatch, tmp_path):
    engine = build_test_engine(monkeypatch, tmp_path, "rules.create", {"name": "Regla rechazada"})
    proposal = asyncio.run(engine.execute("Crear regla"))
    rejected = engine.confirm_task_operation(proposal.metadata["confirmation_token"], approved=False)
    assert rejected.success is True
    assert rejected.output["status"] == "cancelled"
    assert engine.rule_capability.store.count() == 0


def test_process_rule_mutations_recheck_authorization(monkeypatch, tmp_path):
    engine = build_test_engine(monkeypatch, tmp_path, "processes.create", {"name": "No autorizado"})
    engine._task_action_authorizer = lambda action: False
    proposal = asyncio.run(engine.execute("Crear proceso"))
    result = engine.confirm_task_operation(proposal.metadata["confirmation_token"], approved=True)
    assert result.success is False
    assert result.output["status"] == "unauthorized"
    assert engine.process_capability.store.count() == 0
