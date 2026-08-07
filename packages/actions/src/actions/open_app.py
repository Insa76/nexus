from __future__ import annotations

from planner.plan import PlanStep

from adapters.windows.app_launcher import (
    WindowsAppLauncher,
)

from actions.base import Action

from planner.execution_context import (
    ExecutionContext,
)


class OpenAppCapability(Action):
    """
    Action para abrir aplicaciones
    del sistema operativo.
    """

    name = "system.open_app"

    def __init__(self) -> None:

        self._launcher = WindowsAppLauncher()

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
            "No application specified."
        )

        return

     success = self._launcher.open(
        application
     )

     if not success:

        context.add_error(
            f"Application '{application}' is not supported."
        )

        return

     context.add_result(
        "application",
        application,
     )

     context.add_result(
        "status",
        "opened",
     )