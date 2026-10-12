from unittest.mock import MagicMock

from engine.cognitive_capabilities import CognitiveCapabilityRouter
from rules.cognitive import RuleCognitiveAccess


def test_rule_capability_router_exposes_rule_operations():
    rule_access = MagicMock(
        spec=RuleCognitiveAccess,
    )

    router = CognitiveCapabilityRouter(
        rule_access=rule_access,
    )

    operations = router.available_operations()

    assert len(operations) == 3

    assert {
        (operation.capability, operation.operation, operation.action)
        for operation in operations
    } == {
        (
            "rules",
            "find_relevant",
            "rules.find_relevant",
        ),
        (
            "rules",
            "get",
            "rules.get",
        ),
        (
            "rules",
            "list",
            "rules.list",
        ),
    }
