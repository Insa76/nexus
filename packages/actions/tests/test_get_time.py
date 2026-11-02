from unittest.mock import patch

import pytest

from actions.get_time import GetTimeAction
from planner.execution_context import ExecutionContext
from planner.objective import Objective
from planner.plan import ExecutionPlan, PlanStep


@pytest.mark.asyncio
async def test_get_time_action_records_local_time() -> None:
    objective = Objective(
        id="objective-time",
        title="Consultar la hora",
        description="Consultar la hora",
    )
    step = PlanStep(
        id="step-time",
        name="Consultar hora",
        description="Obtener la hora local",
        action="system.get_time",
    )
    plan = ExecutionPlan(
        objective_id=objective.id,
        steps=[step],
    )
    context = ExecutionContext(
        objective=objective,
        plan=plan,
    )

    with patch("actions.get_time.datetime") as mocked_datetime:
        mocked_datetime.now.return_value.strftime.side_effect = [
            "28/10/2026",
            "14:35",
        ]
        await GetTimeAction().execute(context, step)

    assert context.results["date"] == "28/10/2026"
    assert context.results["time"] == "14:35"
    assert context.results["status"] == "read"
