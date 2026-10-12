from __future__ import annotations

import asyncio

from planner.decision import DecisionEngine
from planner.intent import Intent
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from planner.verification import Verifier
from runtime.execution_result import ExecutionResult


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_verifier_success() -> None:

    verifier = Verifier()

    class Objective:
        id = "objective-1"

    plan = ExecutionPlan(
        objective_id="objective-1",
        steps=[
            PlanStep(
                id="step-1",
                name="test",
                description="test",
                action="system.test",
                status=StepStatus.COMPLETED,
            )
        ],
        completed=True,
    )

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "status": "ok",
        },
    )

    verification = verifier.verify(
        objective=Objective(),
        plan=plan,
        result=result,
    )

    check(
        verification.verified,
        "Successful completed execution must verify.",
    )

    check(
        verification.confidence == 1.0,
        "Expected full verification confidence.",
    )


def test_verifier_failed_execution() -> None:

    verifier = Verifier()

    class Objective:
        id = "objective-2"

    plan = ExecutionPlan(
        objective_id="objective-2",
        completed=True,
    )

    result = ExecutionResult(
        success=False,
        message="execution failed",
        output={},
    )

    verification = verifier.verify(
        objective=Objective(),
        plan=plan,
        result=result,
    )

    check(
        not verification.verified,
        "Failed execution must not verify.",
    )


def test_verifier_incomplete_plan() -> None:

    verifier = Verifier()

    class Objective:
        id = "objective-3"

    plan = ExecutionPlan(
        objective_id="objective-3",
        completed=False,
    )

    result = ExecutionResult(
        success=True,
        message="",
        output={
            "status": "ok",
        },
    )

    verification = verifier.verify(
        objective=Objective(),
        plan=plan,
        result=result,
    )

    check(
        not verification.verified,
        "Incomplete plan must not verify.",
    )


def test_decision_known_action() -> None:

    engine = DecisionEngine()

    intent = Intent(
        action="system.open_app",
        confidence=1.0,
        parameters={
            "application": "chrome",
        },
        original_text="Abrí Chrome",
    )

    decision = engine.decide(
        intent=intent,
        capabilities=[],
    )

    check(
        decision.is_executable,
        "Known action should be executable.",
    )

    check(
        decision.selected_action
        == "system.open_app",
        "Decision selected wrong action.",
    )


async def main() -> None:

    test_verifier_success()
    test_verifier_failed_execution()
    test_verifier_incomplete_plan()
    test_decision_known_action()

    print(
        "ENGINE VERIFICATION INTEGRATION PASSED : 4 FAILED : 0"
    )


if __name__ == "__main__":
    asyncio.run(main())
