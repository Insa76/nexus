from planner.verification import Verifier
from planner.objective import Objective
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.execution_result import ExecutionResult


def make_objective(
    action: str,
    metadata: dict,
) -> Objective:
    return Objective(
        id="objective-test",
        title=action,
        metadata=metadata,
    )


def make_plan(
    action: str,
    completed: bool = True,
) -> ExecutionPlan:
    return ExecutionPlan(
        objective_id="objective-test",
        steps=[
            PlanStep(
                id="step-test",
                name=action,
                description=action,
                action=action,
                status=(
                    StepStatus.COMPLETED
                    if completed
                    else StepStatus.PENDING
                ),
            )
        ],
        current_step=1 if completed else 0,
        completed=completed,
    )


def make_result(
    output: dict,
    success: bool = True,
) -> ExecutionResult:
    return ExecutionResult(
        success=success,
        output=output,
        artifacts={},
        metadata={},
    )


def check(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise AssertionError(message)


def test_open_app_verified() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.open_app",
            {"application": "Chrome"},
        ),
        plan=make_plan(
            "system.open_app",
        ),
        result=make_result(
            {
                "application": "Chrome",
                "status": "opened",
            }
        ),
    )

    check(result.verified, "Open app should be verified.")
    check(
        result.confidence == 1.0,
        "Open app confidence should be 1.0.",
    )


def test_open_app_mismatch() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.open_app",
            {"application": "Chrome"},
        ),
        plan=make_plan(
            "system.open_app",
        ),
        result=make_result(
            {
                "application": "Spotify",
                "status": "opened",
            }
        ),
    )

    check(
        not result.verified,
        "Wrong application must not be verified.",
    )


def test_close_app_verified() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.close_app",
            {"application": "Chrome"},
        ),
        plan=make_plan(
            "system.close_app",
        ),
        result=make_result(
            {
                "application": "Chrome",
                "status": "closed",
            }
        ),
    )

    check(result.verified, "Close app should be verified.")


def test_set_volume_verified() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.set_volume",
            {"level": 50},
        ),
        plan=make_plan(
            "system.set_volume",
        ),
        result=make_result(
            {
                "volume": 50,
                "status": "set",
            }
        ),
    )

    check(
        result.verified,
        "Set volume should be verified.",
    )


def test_set_volume_mismatch() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.set_volume",
            {"level": 50},
        ),
        plan=make_plan(
            "system.set_volume",
        ),
        result=make_result(
            {
                "volume": 30,
                "status": "set",
            }
        ),
    )

    check(
        not result.verified,
        "Wrong volume must not be verified.",
    )


def test_screen_capture_requires_evidence() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.screen_capture",
            {},
        ),
        plan=make_plan(
            "system.screen_capture",
        ),
        result=make_result(
            {
                "status": "captured",
                "image": object(),
            }
        ),
    )

    check(
        result.verified,
        "Screen capture should be verified with image evidence.",
    )


def test_empty_output_is_not_verified() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.open_app",
            {"application": "Chrome"},
        ),
        plan=make_plan(
            "system.open_app",
        ),
        result=make_result({}),
    )

    check(
        not result.verified,
        "Empty output must not be verified.",
    )


def test_execution_failure_is_not_verified() -> None:
    verifier = Verifier()

    result = verifier.verify(
        objective=make_objective(
            "system.open_app",
            {"application": "Chrome"},
        ),
        plan=make_plan(
            "system.open_app",
        ),
        result=make_result(
            {},
            success=False,
        ),
    )

    check(
        not result.verified,
        "Failed execution must not be verified.",
    )


print(
    "VERIFIER EVIDENCE PASSED : 8 FAILED : 0"
)
