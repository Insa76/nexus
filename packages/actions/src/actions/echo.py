from __future__ import annotations

from actions.base import Action

from planner.execution_context import ExecutionContext


class EchoCapability(Action):
    """
    Action de prueba.

    Devuelve exactamente el texto recibido
    en el Objective.
    """

    name = "echo"

    async def execute(
        self,
        context: ExecutionContext,
    ) -> None:

        context.add_result(

            "response",

            context.objective.description,

        )