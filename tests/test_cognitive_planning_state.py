import asyncio

from planner.execution_context import ExecutionContext
from planner.objective import Objective, ObjectiveStatus
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.executor import Executor


class FakeActionManager:
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

        context.results[step.id] = {
            "status": "completed"
        }

        for artifact in step.produces:
            context.artifacts[artifact] = {
                "produced_by": step.id
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
        id="objective-state-test",
        title="State Consistency Test",
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


def test_successful_plan_has_consistent_global_state():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
            ),
            make_step(
                "step_b",
                "action_b",
                depends_on=["step_a"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True

    assert context.finished is True
    assert context.plan.completed is True
    assert (
        context.objective.status
        == ObjectiveStatus.COMPLETED
    )

    assert all(
        step.status == StepStatus.COMPLETED
        for step in context.plan.steps
    )


def test_successful_steps_match_execution_results():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
            ),
            make_step(
                "step_b",
                "action_b",
                depends_on=["step_a"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True

    for step in context.plan.steps:
        assert step.status == StepStatus.COMPLETED
        assert step.id in result.output
        assert result.output[step.id][
            "status"
        ] == "completed"


def test_failed_execution_has_consistent_global_state():
    runtime = FakeRuntime(
        failing_steps={"step_b"}
    )

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
            ),
            make_step(
                "step_b",
                "action_b",
                depends_on=["step_a"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False

    assert context.finished is True
    assert context.plan.completed is False
    assert (
        context.objective.status
        == ObjectiveStatus.FAILED
    )

    assert (
        get_step(context, "step_a").status
        == StepStatus.COMPLETED
    )

    assert (
        get_step(context, "step_b").status
        == StepStatus.FAILED
    )


def test_failed_execution_does_not_report_success():
    runtime = FakeRuntime(
        failing_steps={"step_a"}
    )

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
            )
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is False
    assert context.plan.completed is False

    assert (
        result.metadata["plan_completed"]
        is False
    )

    assert (
        result.metadata["objective_status"]
        == ObjectiveStatus.FAILED.value
    )


def test_execution_metadata_matches_context_state():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
            ),
            make_step(
                "step_b",
                "action_b",
                depends_on=["step_a"],
            ),
            make_step(
                "step_c",
                "action_c",
                depends_on=["step_b"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True

    metadata = result.metadata

    assert (
        metadata["objective_id"]
        == context.objective.id
    )

    assert (
        metadata["objective_status"]
        == context.objective.status.value
    )

    assert (
        metadata["plan_completed"]
        == context.plan.completed
    )

    assert (
        metadata["step_count"]
        == len(context.plan.steps)
    )

    assert (
        metadata["errors"]
        == context.errors
    )


def test_current_step_and_completed_steps_remain_coherent():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
            ),
            make_step(
                "step_b",
                "action_b",
            ),
            make_step(
                "step_c",
                "action_c",
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True

    completed_count = sum(
        1
        for step in context.plan.steps
        if step.status == StepStatus.COMPLETED
    )

    assert (
        context.current_step
        == completed_count
    )

    assert (
        context.current_step
        == len(context.plan.steps)
    )


def main():
    tests = [
        (
            "test_successful_plan_has_consistent_global_state",
            test_successful_plan_has_consistent_global_state,
        ),
        (
            "test_successful_steps_match_execution_results",
            test_successful_steps_match_execution_results,
        ),
        (
            "test_failed_execution_has_consistent_global_state",
            test_failed_execution_has_consistent_global_state,
        ),
        (
            "test_failed_execution_does_not_report_success",
            test_failed_execution_does_not_report_success,
        ),
        (
            "test_execution_metadata_matches_context_state",
            test_execution_metadata_matches_context_state,
        ),
        (
            "test_current_step_and_completed_steps_remain_coherent",
            test_current_step_and_completed_steps_remain_coherent,
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
        f"COGNITIVE PLANNING 6.6: "
        f"{passed}/{len(tests)} PASSED"
    )


if __name__ == "__main__":
    main()
