
from context import AssistantContext
from engine.cognitive_capabilities import CognitiveCapabilityRouter
from rules.capability import RuleCapability
from rules.cognitive import RuleCognitiveAccess
from rules.resolver import RuleResolver
from rules.store import RuleStore


class User:
    def __init__(self, user_id: str):
        self.id = user_id


def test_router_executes_real_rule_cognitive_cycle():
    store = RuleStore()
    resolver = RuleResolver(store)
    capability = RuleCapability(
        store=store,
        resolver=resolver,
    )
    cognitive_access = RuleCognitiveAccess(capability)
    router = CognitiveCapabilityRouter(
        rule_access=cognitive_access,
    )

    rule = capability.create(
        name="Regla de prueba",
        description="Regla relevante para el contexto actual.",
        user_id="user-1",
    )

    context = AssistantContext(
        user=User("user-1"),
        organization=None,
        projects=(),
    )

    invocation = router.select(
        action="rules.find_relevant",
        parameters={},
    )

    assert invocation is not None
    assert invocation.capability == "rules"
    assert invocation.operation == "find_relevant"

    result = router.invoke(
        invocation,
        context=context,
         assistant_context=context,
    )

    assert result.rules == (rule,)
    assert result.metadata["operation"] == "rules.find_relevant"
    assert result.metadata["count"] == 1

    summary = router.summarize_operation_result(
        result,
        operation=invocation.operation,
    )

    assert summary["operation"] == "rules.find_relevant"
    assert summary["result_count"] == 1
    assert summary["has_results"] is True
    assert summary["status"] == "found"
