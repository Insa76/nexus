from __future__ import annotations

from actions.base import Action

from planner.execution_context import ExecutionContext
from planner.plan import PlanStep


class EchoAction(Action):
    """
    Action de prueba.

    Devuelve exactamente el texto recibido
    en el Objective.
    """

    name = "echo"

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:

        context.add_result(
            "response",
            context.objective.description,
        )
