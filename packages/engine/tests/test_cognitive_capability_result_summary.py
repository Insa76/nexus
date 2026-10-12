from __future__ import annotations

from engine.cognitive_capabilities import (
    CognitiveCapabilityRouter,
)
from processes.models import Process
from rules.models import Rule


def test_summarize_process_get_result() -> None:
    process = Process.create(
        name="Proceso de prueba",
        description="Descripción",
    )

    summary = CognitiveCapabilityRouter.summarize_operation_result(
        process,
        operation="processes.get",
    )

    assert summary == {
        "operation": "processes.get",
        "result_count": 1,
        "has_results": True,
        "status": "found",
    }


def test_summarize_process_list_result() -> None:
    processes = (
        Process.create(
            name="Proceso 1",
            description="Descripción 1",
        ),
        Process.create(
            name="Proceso 2",
            description="Descripción 2",
        ),
    )

    summary = CognitiveCapabilityRouter.summarize_operation_result(
        processes,
        operation="processes.list",
    )

    assert summary == {
        "operation": "processes.list",
        "result_count": 2,
        "has_results": True,
        "status": "found",
    }


def test_summarize_empty_process_list_result() -> None:
    summary = CognitiveCapabilityRouter.summarize_operation_result(
        (),
        operation="processes.list",
    )

    assert summary == {
        "operation": "processes.list",
        "result_count": 0,
        "has_results": False,
        "status": "empty",
    }


def test_summarize_rule_get_result() -> None:
    rule = Rule.create(
        name="Regla de prueba",
        description="Descripción",
    )

    summary = CognitiveCapabilityRouter.summarize_operation_result(
        rule,
        operation="rules.get",
    )

    assert summary == {
        "operation": "rules.get",
        "result_count": 1,
        "has_results": True,
        "status": "found",
    }


def test_summarize_rule_list_result() -> None:
    rules = (
        Rule.create(
            name="Regla 1",
            description="Descripción 1",
        ),
        Rule.create(
            name="Regla 2",
            description="Descripción 2",
        ),
    )

    summary = CognitiveCapabilityRouter.summarize_operation_result(
        rules,
        operation="rules.list",
    )

    assert summary == {
        "operation": "rules.list",
        "result_count": 2,
        "has_results": True,
        "status": "found",
    }


def test_summarize_empty_rule_list_result() -> None:
    summary = CognitiveCapabilityRouter.summarize_operation_result(
        (),
        operation="rules.list",
    )

    assert summary == {
        "operation": "rules.list",
        "result_count": 0,
        "has_results": False,
        "status": "empty",
    }
