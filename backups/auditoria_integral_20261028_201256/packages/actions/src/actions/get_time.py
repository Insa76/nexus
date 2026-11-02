from __future__ import annotations

from datetime import datetime

from actions.base import Action
from planner.execution_context import ExecutionContext
from planner.plan import PlanStep


class GetTimeAction(Action):
    """Acción para consultar la fecha y hora local del equipo."""

    name = "system.get_time"
    description = "Consultar la fecha y hora local del sistema."
    internal = True

    produces = ["date", "time"]

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y")
        current_time = now.strftime("%H:%M")

        context.add_result("date", current_date)
        context.add_result("time", current_time)
        context.add_result("status", "read")
