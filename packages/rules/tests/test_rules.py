from context import AssistantContext

from rules.models import Rule, RuleStatus
from rules.resolver import RuleResolver
from rules.store import RuleStore
from rules import RuleCapability
from rules import RuleCognitiveAccess



def test_rule_create():
    rule = Rule.create(
        name="Regla de aprobación",
        description="Requiere aprobación antes de continuar",
    )

    assert rule.id
    assert rule.name == "Regla de aprobación"
    assert rule.description == (
        "Requiere aprobación antes de continuar"
    )
    assert rule.status == RuleStatus.ACTIVE


def test_rule_store():
    store = RuleStore()

    rule = Rule.create(
        name="Regla operativa",
    )

    store.add(rule)

    assert store.get(rule.id) == rule
    assert store.list() == [rule]
    assert store.count() == 1

    updated = Rule(
        id=rule.id,
        name=rule.name,
        description=rule.description,
        status=RuleStatus.INACTIVE,
        user_id=rule.user_id,
        organization_id=rule.organization_id,
        project_id=rule.project_id,
        created_at=rule.created_at,
    )

    store.update(updated)

    assert store.get(rule.id).status == RuleStatus.INACTIVE

    removed = store.remove(rule.id)

    assert removed == updated
    assert store.count() == 0


def test_rule_resolver_by_user():
    store = RuleStore()

    rule = Rule.create(
        name="Regla personal",
        user_id="user-1",
    )

    store.add(rule)

    context = AssistantContext(
        user=type("User", (), {"id": "user-1"})(),
        organization=None,
        projects=[],
    )

    resolver = RuleResolver(store)

    resolved = resolver.resolve(context)

    assert resolved == [rule]

def test_rule_capability():
    store = RuleStore()
    resolver = RuleResolver(store)

    capability = RuleCapability(
        store=store,
        resolver=resolver,
    )

    rule = capability.create(
        name="Regla operativa",
        description="Regla creada mediante capability",
    )

    assert rule.name == "Regla operativa"
    assert capability.get(rule.id) == rule
    assert capability.list() == [rule]

    removed = capability.remove(rule.id)

    assert removed == rule
    assert capability.list() == []

def test_rule_cognitive_access():
    store = RuleStore()
    resolver = RuleResolver(store)

    capability = RuleCapability(
        store=store,
        resolver=resolver,
    )

    rule = capability.create(
        name="Regla contextual",
        user_id="user-1",
    )

    access = RuleCognitiveAccess(capability)

    context = AssistantContext(
        user=type("User", (), {"id": "user-1"})(),
        organization=None,
        projects=[],
    )

    result = access.find_relevant(
        context=context,
    )

    assert result.rules == (rule,)
    assert result.metadata["operation"] == "rules.find_relevant"
    assert result.metadata["count"] == 1
