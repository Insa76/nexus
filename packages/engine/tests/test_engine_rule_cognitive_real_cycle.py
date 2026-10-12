import pytest

from context import AssistantContext
from rules.capability import RuleCapability
from rules.cognitive import RuleCognitiveAccess
from rules.resolver import RuleResolver
from rules.store import RuleStore


class User:
    def __init__(self, user_id: str):
        self.id = user_id


@pytest.mark.asyncio
async def test_engine_executes_real_rule_cognitive_cycle():
    store = RuleStore()
    resolver = RuleResolver(store)
    capability = RuleCapability(
        store=store,
        resolver=resolver,
    )
    cognitive_access = RuleCognitiveAccess(capability)

    rule = capability.create(
        name="Regla de prueba",
        description="Regla relevante para el contexto actual.",
        user_id="user-1",
    )

    context = AssistantContext(
        user=User("user-1"),
        organization=None,
        projects=[],
    )

    result = cognitive_access.find_relevant(context=context)

    assert result.rules == (rule,)
    assert result.metadata["operation"] == "rules.find_relevant"
    assert result.metadata["count"] == 1
