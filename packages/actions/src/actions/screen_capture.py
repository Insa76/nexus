from __future__ import annotations

from adapters.windows.screen_capture import (
    WindowsScreenCaptureAdapter,
)

from actions.base import Action
from packages.planner.src.planner.plan import PlanStep
from packages.planner.src.planner.execution_context import ExecutionContext


class ScreenCaptureAction(Action):

    name = "system.screen_capture"

    def __init__(self):

        self._adapter = WindowsScreenCaptureAdapter()

    async def execute(

        self,

        context: ExecutionContext,

        step: PlanStep,

    ) -> None:

        image = self._adapter.capture()

        path = step.metadata.get(
            "path"
        )

        if path:

            image.save(path)

            context.add_result(

                "path",

                path,
            )

        context.add_result(

            "image",

            image,
        )

        context.add_result(

            "status",

            "captured",
        )