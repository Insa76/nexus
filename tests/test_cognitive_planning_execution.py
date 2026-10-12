import asyncio

from planner.execution_context import ExecutionContext
from planner.objective import Objective, ObjectiveStatus
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.executor import Executor


class FakeActionManager:
    """
    ActionManager mínimo para probar el Executor real.

    No reemplaza la lógica del Executor:
    solamente ejecuta el step que éste selecciona.
    """

    def __init__(self):
        self.execution_order = []

    async def execute(self, context):
        step = context.plan.steps[context.current_step]

        self.execution_order.append(step.id)

        step.status = StepStatus.COMPLETED

        # Registrar el resultado producido por el step.
        for artifact in step.produces:
            context.artifacts[artifact] = {
                "produced_by": step.id
            }

        context.results[step.id] = {
            "status": "completed"
        }


class FakeRuntime:
    def __init__(self):
        self.action_manager = FakeActionManager()


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
        produces=produces or [],
        consumes=consumes or [],
    )


def make_context(steps):
    objective = Objective(
        id="objective-test",
        title="Cognitive Planning Execution Test",
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


def test_simple_plan_executes():
    runtime = FakeRuntime()

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

    assert result.success is True
    assert context.plan.completed is True
    assert context.objective.status == ObjectiveStatus.COMPLETED

    assert (
        context.plan.steps[0].status
        == StepStatus.COMPLETED
    )

    assert (
        runtime.action_manager.execution_order
        == ["step_a"]
    )


def test_linear_dependency_chain_executes_in_order():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
                produces=["artifact_a"],
            ),
            make_step(
                "step_b",
                "action_b",
                depends_on=["step_a"],
                consumes=["artifact_a"],
                produces=["artifact_b"],
            ),
            make_step(
                "step_c",
                "action_c",
                depends_on=["step_b"],
                consumes=["artifact_b"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True
    assert context.plan.completed is True

    assert (
        runtime.action_manager.execution_order
        == [
            "step_a",
            "step_b",
            "step_c",
        ]
    )


def test_dependency_can_execute_even_when_declared_later():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "consumer",
                "consumer",
                depends_on=["producer"],
                consumes=["artifact_a"],
            ),
            make_step(
                "producer",
                "producer",
                produces=["artifact_a"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True
    assert context.plan.completed is True

    assert (
        runtime.action_manager.execution_order
        == [
            "producer",
            "consumer",
        ]
    )


def test_independent_steps_can_execute_without_dependency():
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
    assert context.plan.completed is True

    assert (
        runtime.action_manager.execution_order
        == [
            "step_a",
            "step_b",
            "step_c",
        ]
    )


def test_branching_dag_executes_all_branches():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "root",
                "root",
                produces=["root_artifact"],
            ),
            make_step(
                "branch_a",
                "branch_a",
                depends_on=["root"],
                consumes=["root_artifact"],
                produces=["artifact_a"],
            ),
            make_step(
                "branch_b",
                "branch_b",
                depends_on=["root"],
                consumes=["root_artifact"],
                produces=["artifact_b"],
            ),
            make_step(
                "join",
                "join",
                depends_on=[
                    "branch_a",
                    "branch_b",
                ],
                consumes=[
                    "artifact_a",
                    "artifact_b",
                ],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True
    assert context.plan.completed is True

    order = runtime.action_manager.execution_order

    assert order[0] == "root"

    assert (
        set(order[1:3])
        == {
            "branch_a",
            "branch_b",
        }
    )

    assert order[3] == "join"


def test_execution_metadata_contains_step_evidence():
    runtime = FakeRuntime()

    context = make_context(
        [
            make_step(
                "step_a",
                "action_a",
                produces=["artifact_a"],
            ),
            make_step(
                "step_b",
                "action_b",
                depends_on=["step_a"],
                consumes=["artifact_a"],
            ),
        ]
    )

    result = run_executor(
        context,
        runtime,
    )

    assert result.success is True
    assert context.plan.completed is True

    assert "step_evidence" in result.metadata

    assert isinstance(
        result.metadata["step_evidence"],
        dict,
    )


def main():
    tests = [
        (
            "test_simple_plan_executes",
            test_simple_plan_executes,
        ),
        (
            "test_linear_dependency_chain_executes_in_order",
            test_linear_dependency_chain_executes_in_order,
        ),
        (
            "test_dependency_can_execute_even_when_declared_later",
            test_dependency_can_execute_even_when_declared_later,
        ),
        (
            "test_independent_steps_can_execute_without_dependency",
            test_independent_steps_can_execute_without_dependency,
        ),
        (
            "test_branching_dag_executes_all_branches",
            test_branching_dag_executes_all_branches,
        ),
        (
            "test_execution_metadata_contains_step_evidence",
            test_execution_metadata_contains_step_evidence,
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
            print(f"      {type(exc).__name__}: {exc}")

    print()
    print(
        f"COGNITIVE PLANNING 6.4: "
        f"{passed}/{len(tests)} PASSED"
    )


if __name__ == "__main__":
    main()
