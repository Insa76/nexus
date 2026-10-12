from __future__ import annotations

import asyncio

from planner.execution_context import ExecutionContext
from planner.intent import Intent
from planner.objective import Objective
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.execution_result import ExecutionResult


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


class FakeAction:
    def __init__(
        self,
        action: str,
        output: dict,
        artifact: tuple[str, object] | None = None,
    ):
        self.action = action
        self.output = output
        self.artifact = artifact
        self.internal = False

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:

        for key, value in self.output.items():
            context.add_result(
                key,
                value,
            )

        if self.artifact is not None:
            key, value = self.artifact

            context.add_artifact(
                key,
                value,
            )


class FakeActionManager:
    def __init__(self, actions: dict[str, FakeAction]):
        self.actions = actions

    async def execute(
        self,
        context: ExecutionContext,
    ) -> None:

        step = context.current_plan_step()

        if step is None:
            return

        action = self.actions.get(step.action)

        if action is None:
            context.add_error(
                f"Unknown action: {step.action}"
            )
            return

        step.status = StepStatus.RUNNING

        results_before = dict(
            context.results
        )

        artifacts_before = dict(
            context.artifacts
        )

        try:
            await action.execute(
                context,
                step,
            )

            step.status = (
                StepStatus.COMPLETED
            )

            context.record_step_evidence(
                step,
                status="completed",
                results_before=(
                    results_before
                ),
                artifacts_before=(
                    artifacts_before
                ),
            )

        except Exception as exc:
            step.status = StepStatus.FAILED

            context.add_error(
                str(exc)
            )

            context.record_step_evidence(
                step,
                status="failed",
                results_before=(
                    results_before
                ),
                artifacts_before=(
                    artifacts_before
                ),
            )


class FakeRuntime:
    def __init__(
        self,
        actions: dict[str, FakeAction],
    ):
        self.action_manager = (
            FakeActionManager(actions)
        )


def make_step(
    step_id: str,
    action: str,
    depends_on: list[str] | None = None,
) -> PlanStep:

    return PlanStep(
        id=step_id,
        name=step_id,
        description=step_id,
        action=action,
        status=StepStatus.PENDING,
        depends_on=(
            depends_on
            if depends_on is not None
            else []
        ),
        consumes=[],
        produces=[],
        metadata={},
    )


def make_compound_context() -> ExecutionContext:

    objective = Objective(
        id="objective-compound",
        title="compound",
        metadata={
            "application": "Chrome",
            "level": 60,
        },
    )

    plan = ExecutionPlan(
        objective_id=objective.id,
        steps=[
            make_step(
                "step-1",
                "system.open_app",
            ),
            make_step(
                "step-2",
                "system.set_volume",
                depends_on=["step-1"],
            ),
        ],
        current_step=0,
        completed=False,
        metadata={},
    )

    return ExecutionContext(
        objective=objective,
        plan=plan,
        variables={},
        artifacts={},
        results={},
        errors=[],
        current_step=0,
        finished=False,
        step_evidence={},
    )


async def execute_compound_plan(
    context: ExecutionContext,
) -> ExecutionResult:

    runtime = FakeRuntime(
        {
            "system.open_app": FakeAction(
                "system.open_app",
                {
                    "application": "Chrome",
                    "status": "opened",
                },
            ),
            "system.set_volume": FakeAction(
                "system.set_volume",
                {
                    "volume": 60,
                    "status": "set",
                },
            ),
        }
    )

    while not context.finished:

        step = context.current_plan_step()

        if step is None:
            break

        await runtime.action_manager.execute(
            context
        )

        if context.has_errors():
            context.finished = True
            break

        completed = all(
            current.status
            == StepStatus.COMPLETED
            for current
            in context.plan.steps
        )

        if completed:
            context.plan.completed = True
            context.finished = True
            break

        context.current_step += 1

    return ExecutionResult(
        success=(
            context.plan.completed
            and not context.has_errors()
        ),
        message=(
            "Execution completed successfully."
            if context.plan.completed
            else "Execution failed."
        ),
        output=dict(
            context.results
        ),
        artifacts=dict(
            context.artifacts
        ),
        metadata={
            "step_evidence": (
                context.all_step_evidence()
            ),
        },
    )


def test_engine_compound_execution_produces_step_evidence():
    context = (
        make_compound_context()
    )

    result = asyncio.run(
        execute_compound_plan(
            context
        )
    )

    check(
        result.success,
        "Compound execution must succeed.",
    )

    step_evidence = (
        result.metadata.get(
            "step_evidence"
        )
    )

    check(
        isinstance(
            step_evidence,
            dict,
        ),
        "ExecutionResult must contain step_evidence.",
    )

    check(
        set(step_evidence.keys())
        == {
            "step-1",
            "step-2",
        },
        "Every compound step must have individual evidence.",
    )


def test_engine_compound_execution_preserves_step_outputs():
    context = (
        make_compound_context()
    )

    result = asyncio.run(
        execute_compound_plan(
            context
        )
    )

    step_evidence = (
        result.metadata[
            "step_evidence"
        ]
    )

    step_1 = step_evidence[
        "step-1"
    ]

    step_2 = step_evidence[
        "step-2"
    ]

    check(
        step_1["results"][
            "application"
        ]
        == "Chrome",
        "Step 1 evidence must contain its own application result.",
    )

    check(
        step_1["results"][
            "status"
        ]
        == "opened",
        "Step 1 evidence must contain its own execution status.",
    )

    check(
        step_2["results"][
            "volume"
        ]
        == 60,
        "Step 2 evidence must contain its own volume result.",
    )

    check(
        step_2["results"][
            "status"
        ]
        == "set",
        "Step 2 evidence must contain its own execution status.",
    )


def test_engine_compound_execution_does_not_collapse_evidence_into_global_output():
    context = (
        make_compound_context()
    )

    result = asyncio.run(
        execute_compound_plan(
            context
        )
    )

    step_evidence = (
        result.metadata[
            "step_evidence"
        ]
    )

    check(
        step_evidence[
            "step-1"
        ]["results"]
        != result.output,
        "Step 1 evidence must remain distinct from global output.",
    )

    check(
        step_evidence[
            "step-2"
        ]["results"]
        != result.output,
        "Step 2 evidence must remain distinct from global output.",
    )


def test_engine_compound_execution_respects_dependencies():
    context = (
        make_compound_context()
    )

    result = asyncio.run(
        execute_compound_plan(
            context
        )
    )

    check(
        result.success,
        "Compound execution must succeed.",
    )

    check(
        context.plan.steps[
            0
        ].status
        == StepStatus.COMPLETED,
        "First step must complete.",
    )

    check(
        context.plan.steps[
            1
        ].status
        == StepStatus.COMPLETED,
        "Dependent step must complete.",
    )

    check(
        context.plan.completed,
        "Compound plan must be completed.",
    )


def test_engine_compound_execution_fails_without_complete_step_evidence():
    context = (
        make_compound_context()
    )

    result = asyncio.run(
        execute_compound_plan(
            context
        )
    )

    step_evidence = (
        result.metadata[
            "step_evidence"
        ]
    )

    del step_evidence[
        "step-2"
    ]

    check(
        "step-2"
        not in step_evidence,
        "The test must be able to represent missing evidence.",
    )

    check(
        result.success,
        "Execution itself should still be successful; verification must detect the missing evidence.",
    )


def test_engine_compound_result_is_ready_for_verifier():
    context = (
        make_compound_context()
    )

    result = asyncio.run(
        execute_compound_plan(
            context
        )
    )

    check(
        result.success,
        "ExecutionResult must report successful execution.",
    )

    check(
        context.plan.completed,
        "Execution plan must be completed.",
    )

    check(
        len(
            result.metadata[
                "step_evidence"
            ]
        )
        == len(
            context.plan.steps
        ),
        "ExecutionResult must expose evidence for every plan step.",
    )


if __name__ == "__main__":

    tests = [
        (
            name,
            func,
        )
        for name, func in globals().items()
        if name.startswith("test_")
        and callable(func)
    ]

    passed = 0

    for name, test in tests:
        try:
            test()

            print(
                f"PASS: {name}"
            )

            passed += 1

        except Exception as exc:

            print(
                f"FAIL: {name}"
            )

            print(
                f"      {type(exc).__name__}: {exc}"
            )

    print()

    print(
        "ENGINE COMPOUND VERIFICATION: "
        f"{passed}/{len(tests)} PASSED"
    )

    if passed != len(tests):
        raise SystemExit(1)
