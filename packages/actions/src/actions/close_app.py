from __future__ import annotations

from actions.base import Action

from planner.execution_context import (
    ExecutionContext,
)

from planner.plan import PlanStep

from adapters.windows.process_manager import (
    WindowsProcessManager,
)


class CloseAppAction(Action):

    name = "system.close_app"

    def __init__(self):

        self._manager = WindowsProcessManager()

    async def execute(

        self,

        context: ExecutionContext,

        step: PlanStep,

    ) -> None:

        application = step.metadata.get(
            "application"
        )

        if not application:

            context.add_error(
                "Application not specified."
            )

            return

        success = self._manager.close(
            application
        )

        if not success:

            context.add_error(

                f"{application} is not running."

            )

            return

        context.add_result(

            "application",

            application,

        )

        context.add_result(

            "status",

            "closed",

        )