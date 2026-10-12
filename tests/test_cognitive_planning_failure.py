import asyncio

from planner.execution_context import ExecutionContext
from planner.objective import Objective, ObjectiveStatus
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.executor import Executor


class FakeActionManager:
    """
    ActionManager de prueba.

    Permite definir qué steps fallan y reproduce el contrato
    que utiliza el Executor real: execute(context).
    """

    def __init__(self, failing_steps=None):
        self.failing_steps = set(failing_steps or [])
        self.execution_order = []

    async def execute(self, context):
        step = context.plan.steps[context.current_step]

        self.execution_order.append(step.id)

        if step.id in self.failing_steps:
            step.status = StepStatus.FAILED

            context.add_error(
                f"Step '{step.id}' failed."
            )

            return

        step.status = StepStatus.COMPLETED

        for artifact in step.produces:
            context.artifacts[artifact] = {
                "produced_by": step.id
            }

        context.results[step.id] = {
            "status": "completed"
        }


class FakeRuntime:
    def __init__(self, failing_steps=None):
        self.action_manager = FakeActionManager(
            failing_steps=failing_steps
        )


def make_step(
    step_id,
    name,
    depends_on=None,
    produces=None,
    consumes=None,
):
    return PlanStep(
        id=step_id,
        name=name,
        description=name,
        action=name,
        status=StepStatus.PENDING,
        depends_on=depends_on or [],
        consumes=consumes or [],
        produces=produces or [],
    )


def make_context(steps):
    objective = Objective(
        id="objective-failure-test",
        title="Failure Propagation Test",
        status=ObjectiveStatus.READY,
        priority=1,
        metadata={},
    )

    plan = ExecutionPlan(
        objective_id=objective.id,
        steps=steps,
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


def run_executor(context, runtime):
    executor = Executor(runtime)

    return asyncio.run(
        executor.execute(context)
    )


def get_step(context, step_id):
    for step in context.plan.steps:
        if step.id == step_id:
            return step

    raise AssertionError(
        f"Step '{step_id}' not found."
    )


def test_root_failure_marks_plan_as_failed():
    runtime = FakeRuntime(
        failing_steps={"root"}
    )

    context = make_context(
        [
            make_step(
                "root",
                "root",
            ),
            make_step(
                "dependent",
                "dependent",
                depends_on=["root"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False
    assert context.plan.completed is False
    assert (
        context.objective.status
        == ObjectiveStatus.FAILED
    )

    assert (
        get_step(context, "root").status
        == StepStatus.FAILED
    )


def test_failed_intermediate_step_stops_execution():
    runtime = FakeRuntime(
        failing_steps={"middle"}
    )

    context = make_context(
        [
            make_step(
                "root",
                "root",
                produces=["artifact_a"],
            ),
            make_step(
                "middle",
                "middle",
                depends_on=["root"],
                consumes=["artifact_a"],
                produces=["artifact_b"],
            ),
            make_step(
                "final",
                "final",
                depends_on=["middle"],
                consumes=["artifact_b"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False
    assert context.plan.completed is False

    assert (
        runtime.action_manager.execution_order
        == [
            "root",
            "middle",
        ]
    )

    assert (
        get_step(context, "root").status
        == StepStatus.COMPLETED
    )

    assert (
        get_step(context, "middle").status
        == StepStatus.FAILED
    )

    assert (
        get_step(context, "final").status
        == StepStatus.PENDING
    )


def test_failed_dependency_blocks_dependent_step():
    runtime = FakeRuntime(
        failing_steps={"producer"}
    )

    context = make_context(
        [
            make_step(
                "producer",
                "producer",
                produces=["artifact_a"],
            ),
            make_step(
                "consumer",
                "consumer",
                depends_on=["producer"],
                consumes=["artifact_a"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False

    assert (
        get_step(context, "producer").status
        == StepStatus.FAILED
    )

    assert (
        get_step(context, "consumer").status
        == StepStatus.PENDING
    )

    assert (
        "consumer"
        not in runtime.action_manager.execution_order
    )


def test_independent_steps_do_not_hide_failure():
    runtime = FakeRuntime(
        failing_steps={"failing"}
    )

    context = make_context(
        [
            make_step(
                "failing",
                "failing",
            ),
            make_step(
                "independent",
                "independent",
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False
    assert context.plan.completed is False

    assert (
        runtime.action_manager.execution_order
        == ["failing"]
    )

    assert (
        get_step(context, "independent").status
        == StepStatus.PENDING
    )


def test_failed_plan_cannot_be_marked_completed():
    runtime = FakeRuntime(
        failing_steps={"step_b"}
    )

    context = make_context(
        [
            make_step(
                "step_a",
                "step_a",
            ),
            make_step(
                "step_b",
                "step_b",
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False
    assert context.plan.completed is False

    assert (
        context.objective.status
        == ObjectiveStatus.FAILED
    )

    assert (
        not all(
            step.status == StepStatus.COMPLETED
            for step in context.plan.steps
        )
    )


def test_failure_metadata_contains_error_and_incomplete_plan():
    runtime = FakeRuntime(
        failing_steps={"root"}
    )

    context = make_context(
        [
            make_step(
                "root",
                "root",
            ),
            make_step(
                "dependent",
                "dependent",
                depends_on=["root"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False

    assert result.metadata[
        "plan_completed"
    ] is False

    assert result.metadata[
        "objective_status"
    ] == ObjectiveStatus.FAILED.value

    assert result.metadata["errors"]

    assert (
        any(
            "root" in error
            for error in result.metadata["errors"]
        )
    )


def main():
    tests = [
        (
            "test_root_failure_marks_plan_as_failed",
            test_root_failure_marks_plan_as_failed,
        ),
        (
            "test_failed_intermediate_step_stops_execution",
            test_failed_intermediate_step_stops_execution,
        ),
        (
            "test_failed_dependency_blocks_dependent_step",
            test_failed_dependency_blocks_dependent_step,
        ),
        (
            "test_independent_steps_do_not_hide_failure",
            test_independent_steps_do_not_hide_failure,
        ),
        (
            "test_failed_plan_cannot_be_marked_completed",
            test_failed_plan_cannot_be_marked_completed,
        ),
        (
            "test_failure_metadata_contains_error_and_incomplete_plan",
            test_failure_metadata_contains_error_and_incomplete_plan,
        ),
    ]

    passed = 0

    for name, test in tests:
        try:
            test()
            print(f"PASS: {name}")
            passed += 1
        except Exception as exc:
            print(f"FAIL: {name}")
            print(
                f"      {type(exc).__name__}: {exc}"
            )

    print()
    print(
        f"COGNITIVE PLANNING 6.5: "
        f"{passed}/{len(tests)} PASSED"
    )


if __name__ == "__main__":
    main()
