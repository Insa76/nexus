from pathlib import Path

from planner.execution_context import ExecutionContext
from planner.objective import Objective, ObjectiveStatus
from planner.plan import ExecutionPlan, PlanStep, StepStatus
from runtime.execution_store import SQLiteExecutionStore


def make_context() -> ExecutionContext:
    objective = Objective(id="objective-1", title="Abrir aplicación")
    plan = ExecutionPlan(
        objective_id=objective.id,
        steps=[
            PlanStep(
                id="step-1",
                name="Abrir",
                description="Abrir aplicación",
                action="system.open_app",
            )
        ],
    )
    return ExecutionContext(
        objective=objective,
        plan=plan,
        request_text="Abrí el bloc de notas",
        actor_id="local-console",
        actor_type="system",
    )


def test_execution_checkpoint_survives_reopen(tmp_path: Path) -> None:
    path = tmp_path / "executions.sqlite3"
    store = SQLiteExecutionStore(path)
    context = make_context()
    store.begin(context)
    context.current_step = 0
    context.plan.steps[0].status = StepStatus.RUNNING
    store.checkpoint(context)
    store.close()

    reopened = SQLiteExecutionStore(path)
    record = reopened.get("objective-1")
    assert record is not None
    assert record["status"] == "running"
    assert record["snapshot"]["plan"]["steps"][0]["status"] == "running"
    reopened.close()


def test_recovery_marks_inflight_execution_interrupted_without_replay(tmp_path: Path) -> None:
    path = tmp_path / "executions.sqlite3"
    store = SQLiteExecutionStore(path)
    context = make_context()
    store.begin(context)
    context.plan.steps[0].status = StepStatus.RUNNING
    store.checkpoint(context)

    assert store.recover_interrupted() == 1
    record = store.get("objective-1")
    assert record is not None
    assert record["status"] == "interrupted"
    assert "Verificá el efecto" in record["error"]
    assert record["snapshot"]["plan"]["steps"][0]["status"] == "running"
    assert store.recover_interrupted() == 0
    store.close()


def test_completed_execution_is_listed_with_step_progress(tmp_path: Path) -> None:
    store = SQLiteExecutionStore(tmp_path / "executions.sqlite3")
    context = make_context()
    store.begin(context)
    context.plan.steps[0].status = StepStatus.COMPLETED
    context.objective.status = ObjectiveStatus.COMPLETED
    context.plan.completed = True
    context.finished = True
    store.checkpoint(context)
    store.finish(context, success=True)

    records = store.list()
    assert len(records) == 1
    assert records[0]["status"] == "completed"
    assert records[0]["completed_steps"] == 1
    store.close()


class CompletingActionManager:
    async def execute(self, context: ExecutionContext) -> None:
        step = context.current_plan_step()
        assert step is not None
        step.status = StepStatus.COMPLETED
        context.results["opened"] = True


async def test_executor_persists_completed_runtime_execution(tmp_path: Path) -> None:
    from types import SimpleNamespace

    from runtime.executor import Executor

    store = SQLiteExecutionStore(tmp_path / "executions.sqlite3")
    runtime = SimpleNamespace(
        action_manager=CompletingActionManager(),
        execution_store=store,
    )
    context = make_context()

    result = await Executor(runtime).execute(context)

    record = store.get("objective-1")
    assert result.success is True
    assert record is not None
    assert record["status"] == "completed"
    assert record["snapshot"]["results"]["opened"] is True
    assert record["snapshot"]["plan"]["steps"][0]["status"] == "completed"
    store.close()
