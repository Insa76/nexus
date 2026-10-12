from unittest.mock import MagicMock

from engine.cognitive_capabilities import (
    CognitiveCapabilityInvocation,
    CognitiveCapabilityRouter,
)
from processes.cognitive import ProcessCognitiveAccess
from rules.cognitive import RuleCognitiveAccess


def test_router_invokes_process_get():
    process_access = MagicMock(
        spec=ProcessCognitiveAccess,
    )

    expected = MagicMock()
    process_access.get.return_value = expected

    router = CognitiveCapabilityRouter(
        process_access=process_access,
    )

    invocation = CognitiveCapabilityInvocation(
        capability="processes",
        operation="get",
        parameters={"process_id": "process-1"},
    )

    result = router.invoke(
        invocation,
        context=MagicMock(),
    )

    assert result is expected
    process_access.get.assert_called_once_with("process-1")


def test_router_invokes_process_list():
    process_access = MagicMock(
        spec=ProcessCognitiveAccess,
    )

    expected = (MagicMock(), MagicMock())
    process_access.list.return_value = expected

    router = CognitiveCapabilityRouter(
        process_access=process_access,
    )

    invocation = CognitiveCapabilityInvocation(
        capability="processes",
        operation="list",
        parameters={},
    )

    result = router.invoke(
        invocation,
        context=MagicMock(),
    )

    assert result is expected
    process_access.list.assert_called_once_with()


def test_router_invokes_rule_get():
    rule_access = MagicMock(
        spec=RuleCognitiveAccess,
    )

    expected = MagicMock()
    rule_access.get.return_value = expected

    router = CognitiveCapabilityRouter(
        rule_access=rule_access,
    )

    invocation = CognitiveCapabilityInvocation(
        capability="rules",
        operation="get",
        parameters={"rule_id": "rule-1"},
    )

    result = router.invoke(
        invocation,
        context=MagicMock(),
    )

    assert result is expected
    rule_access.get.assert_called_once_with("rule-1")


def test_router_invokes_rule_list():
    rule_access = MagicMock(
        spec=RuleCognitiveAccess,
    )

    expected = (MagicMock(), MagicMock())
    rule_access.list.return_value = expected

    router = CognitiveCapabilityRouter(
        rule_access=rule_access,
    )

    invocation = CognitiveCapabilityInvocation(
        capability="rules",
        operation="list",
        parameters={},
    )

    result = router.invoke(
        invocation,
        context=MagicMock(),
    )

    assert result is expected
    rule_access.list.assert_called_once_with()
