from __future__ import annotations

from uuid import uuid4

from planner.intent import Intent
from planner.objective import (
    Objective,
    ObjectiveStatus,
)
from planner.plan import (
    ExecutionPlan,
    PlanStep,
)


class Planner:
    """
    Convierte un Intent en un ExecutionPlan.
    """

    def create_plan(
        self,
        objective: Objective,
        intent: Intent,
    ) -> ExecutionPlan:

        objective.status = ObjectiveStatus.PLANNING

        plan = ExecutionPlan(
            objective_id=objective.id,
        )

        step = PlanStep(

            id=str(uuid4()),

            name=intent.action,

            description=objective.title,

            action=intent.action,

            metadata=intent.parameters.copy(),

        )

        plan.steps.append(step)

        objective.status = ObjectiveStatus.READY

        return plan