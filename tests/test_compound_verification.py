from planner.objective import Objective
from planner.plan import (
    ExecutionPlan,
    PlanStep,
    StepStatus,
)
from planner.verification import Verifier
from runtime.execution_result import ExecutionResult


def make_step(
    step_id: str,
    action: str,
    result_keys=None,
    artifact_keys=None,
):
    metadata = {
        "execution": {
            "status": "completed",
            "result_keys": result_keys or [],
            "artifact_keys": artifact_keys or [],
        }
    }

    return PlanStep(
        id=step_id,
        name=action,
        description=action,
        action=action,
        status=StepStatus.COMPLETED,
        metadata=metadata,
    )


def make_plan(steps):
    return ExecutionPlan(
        objective_id="objective-test",
        steps=steps,
        current_step=len(steps),
        completed=True,
    )


def make_result(
    output=None,
    artifacts=None,
    step_evidence=None,
    success=True,
):
    metadata = {}

    if step_evidence is not None:
        metadata["step_evidence"] = step_evidence

    return ExecutionResult(
        success=success,
        message="",
        output=output or {},
        artifacts=artifacts or {},
        metadata=metadata,
    )


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def test_compound_plan_all_steps_verified():
    objective = Objective(
        id="objective-test",
        title="compound",
        metadata={
            "application": "Chrome",
            "level": 60,
        },
    )

    plan = make_plan(
        [
            make_step(
                "step-1",
                "system.open_app",
                result_keys=["application", "status"],
            ),
            make_step(
                "step-2",
                "system.set_volume",
                result_keys=["volume", "status"],
            ),
            make_step(
                "step-3",
                "system.screen_capture",
                result_keys=["status"],
                artifact_keys=["image"],
            ),
        ]
    )

    result = make_result(
        output={
            "application": "Chrome",
            "status": "opened",
            "volume": 60,
        },
        artifacts={
            "image": object(),
        },
        step_evidence={
            "step-1": {
                "step_id": "step-1",
                "action": "system.open_app",
                "status": "completed",
                "results": {
                    "application": "Chrome",
                    "status": "opened",
                },
                "artifacts": {},
            },
            "step-2": {
                "step_id": "step-2",
                "action": "system.set_volume",
                "status": "completed",
                "results": {
                    "volume": 60,
                    "status": "set",
                },
                "artifacts": {},
            },
            "step-3": {
                "step_id": "step-3",
                "action": "system.screen_capture",
                "status": "completed",
                "results": {
                    "status": "captured",
                },
                "artifacts": {
                    "image": object(),
                },
            },
        },
    )

    verification = Verifier().verify(
        objective,
        plan,
        result,
    )

    check(
        verification.verified,
        "All compound steps should be verified.",
    )

    check(
        verification.metadata["steps_verified"] == 3,
        "All three steps should be verified.",
    )

    check(
        verification.metadata["steps_total"] == 3,
        "Plan should contain three steps.",
    )


def test_compound_plan_fails_when_one_step_has_wrong_evidence():
    objective = Objective(
        id="objective-test",
        title="compound",
        metadata={
            "application": "Chrome",
            "level": 60,
        },
    )

    plan = make_plan(
        [
            make_step(
                "step-1",
                "system.open_app",
                result_keys=["application", "status"],
            ),
            make_step(
                "step-2",
                "system.set_volume",
                result_keys=["volume", "status"],
            ),
        ]
    )

    result = make_result(
        output={
            "application": "Chrome",
            "status": "opened",
            "volume": 30,
        },
        step_evidence={
            "step-1": {
                "step_id": "step-1",
                "action": "system.open_app",
                "status": "completed",
                "results": {
                    "application": "Chrome",
                    "status": "opened",
                },
                "artifacts": {},
            },
            "step-2": {
                "step_id": "step-2",
                "action": "system.set_volume",
                "status": "completed",
                "results": {
                    "volume": 30,
                    "status": "set",
                },
                "artifacts": {},
            },
        },
    )

    verification = Verifier().verify(
        objective,
        plan,
        result,
    )

    check(
        not verification.verified,
        "Wrong evidence in one step must invalidate the compound plan.",
    )


def test_compound_plan_fails_when_step_evidence_is_missing():
    objective = Objective(
        id="objective-test",
        title="compound",
        metadata={
            "application": "Chrome",
            "level": 60,
        },
    )

    plan = make_plan(
        [
            make_step(
                "step-1",
                "system.open_app",
                result_keys=["application", "status"],
            ),
            make_step(
                "step-2",
                "system.set_volume",
                result_keys=["volume", "status"],
            ),
        ]
    )

    result = make_result(
        output={
            "application": "Chrome",
            "status": "opened",
            "volume": 60,
        },
        step_evidence={
            "step-1": {
                "step_id": "step-1",
                "action": "system.open_app",
                "status": "completed",
                "results": {
                    "application": "Chrome",
                    "status": "opened",
                },
                "artifacts": {},
            },
        },
    )

    verification = Verifier().verify(
        objective,
        plan,
        result,
    )

    check(
        not verification.verified,
        "Missing evidence for one step must invalidate the compound plan.",
    )


def test_compound_plan_fails_when_step_execution_status_is_failed():
    objective = Objective(
        id="objective-test",
        title="compound",
        metadata={
            "application": "Chrome",
            "level": 60,
        },
    )

    failed_step = make_step(
        "step-2",
        "system.set_volume",
        result_keys=["volume", "status"],
    )

    failed_step.status = StepStatus.FAILED
    failed_step.metadata["execution"]["status"] = "failed"

    plan = make_plan(
        [
            make_step(
                "step-1",
                "system.open_app",
                result_keys=["application", "status"],
            ),
            failed_step,
        ]
    )

    result = make_result(
        output={
            "application": "Chrome",
            "status": "opened",
        },
        step_evidence={
            "step-1": {
                "step_id": "step-1",
                "action": "system.open_app",
                "status": "completed",
                "results": {
                    "application": "Chrome",
                    "status": "opened",
                },
                "artifacts": {},
            },
            "step-2": {
                "step_id": "step-2",
                "action": "system.set_volume",
                "status": "failed",
                "results": {},
                "artifacts": {},
            },
        },
    )

    verification = Verifier().verify(
        objective,
        plan,
        result,
    )

    check(
        not verification.verified,
        "Failed step must invalidate the compound plan.",
    )


def test_compound_plan_keeps_single_step_compatibility():
    objective = Objective(
        id="objective-test",
        title="system.open_app",
        metadata={
            "application": "Chrome",
        },
    )

    plan = make_plan(
        [
            make_step(
                "step-1",
                "system.open_app",
                result_keys=["application", "status"],
            )
        ]
    )

    result = make_result(
        output={
            "application": "Chrome",
            "status": "opened",
        },
    )

    verification = Verifier().verify(
        objective,
        plan,
        result,
    )

    check(
        verification.verified,
        "Existing single-step verification must remain valid.",
    )


def test_compound_plan_does_not_accept_global_output_as_step_evidence():
    objective = Objective(
        id="objective-test",
        title="compound",
        metadata={
            "application": "Chrome",
            "level": 60,
        },
    )

    plan = make_plan(
        [
            make_step(
                "step-1",
                "system.open_app",
                result_keys=["application", "status"],
            ),
            make_step(
                "step-2",
                "system.set_volume",
                result_keys=["volume", "status"],
            ),
        ]
    )

    # El output global contiene la evidencia correcta,
    # pero NO existe evidencia individual para los steps.
    result = make_result(
        output={
            "application": "Chrome",
            "status": "opened",
            "volume": 60,
        },
        step_evidence={},
    )

    verification = Verifier().verify(
        objective,
        plan,
        result,
    )

    check(
        not verification.verified,
        "Global output alone must not satisfy compound step verification.",
    )


if __name__ == "__main__":
    tests = [
        (name, func)
        for name, func in globals().items()
        if name.startswith("test_")
        and callable(func)
    ]

    passed = 0

    for name, test in tests:
        try:
            test()
            print(f"PASS: {name}")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {name}")
            print(f"      {type(exc).__name__}: {exc}")

    print()
    print(
        f"COMPOUND VERIFICATION: "
        f"{passed}/{len(tests)} PASSED"
    )

    if passed != len(tests):
        raise SystemExit(1)
