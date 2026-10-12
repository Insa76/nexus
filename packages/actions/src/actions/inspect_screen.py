from __future__ import annotations

from actions.base import Action

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext


class InspectScreenAction(Action):
    """
    Action para inspeccionar una captura de pantalla
    disponible como artifact del contexto.
    """

    name = "system.inspect_screen"

    internal = True

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:

        image = context.get_artifact(
            "image"
        )

        if image is None:

            context.add_error(
                "No screen image artifact available."
            )

            return

        try:

            width, height = image.size

        except Exception as exc:

            context.add_error(
                f"Failed to inspect screen image: {exc}"
            )

            return

        context.add_result(
            "status",
            "inspected",
        )

        context.add_result(
            "image_width",
            width,
        )

        context.add_result(
            "image_height",
            height,
        )
