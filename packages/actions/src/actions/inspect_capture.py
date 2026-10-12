from __future__ import annotations

from typing import Any

from actions.base import Action
from planner.execution_context import ExecutionContext
from planner.plan import PlanStep


class InspectCaptureAction(Action):
    """
    Inspecciona la captura de pantalla disponible
    en los artifacts del ExecutionContext.

    Esta Action es una capacidad cognitiva interna
    de NEXUS.

    Consume:
        image

    Produce:
        capture_inspection
    """

    name = "system.inspect_capture"

    description = (
        "Inspecciona una captura de pantalla previamente "
        "realizada y obtiene información sobre ella."
    )

    parameters: dict[str, Any] = {}

    internal = True

    produces = [
        "capture_inspection",
    ]

    consumes = [
        "image",
    ]

    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:
        image = context.artifacts.get("image")

        if image is None:
            context.add_error(
                "Missing required artifact(s) for "
                f"step '{step.action}': image"
            )
            return

        try:
            width, height = image.size
        except Exception as exc:
            context.add_error(
                f"Failed to inspect captured image: {exc}"
            )
            return

        inspection = {
            "width": width,
            "height": height,
            "status": "inspected",
        }

        context.add_result(
            "capture_inspection",
            inspection,
        )

        context.add_result(
            "width",
            width,
        )

        context.add_result(
            "height",
            height,
        )

        context.add_result(
            "status",
            "inspected",
        )
