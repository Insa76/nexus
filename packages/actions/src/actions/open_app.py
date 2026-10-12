from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from providers.provider_manager import ProviderManager


class OpenAppAction(Action):
    """
    Action para abrir aplicaciones
    del sistema operativo.

    La Action no conoce directamente
    los adapters de Windows.

    Delega la ejecución al ProviderManager.
    """

    name = "system.open_app"

    def __init__(
        self,
        provider_manager: ProviderManager,
    ) -> None:

        self._provider_manager = provider_manager

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

        try:

            success = await self._provider_manager.execute(
                provider="local",
                tool="windows.open_app",
                parameters={
                    "application": application,
                },
            )

        except Exception as exc:

            context.add_error(
                f"Failed to open application "
                f"'{application}': {exc}"
            )

            return

        if not success:

            context.add_error(
                f"Application '{application}' "
                f"is not supported."
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
