from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from providers.provider_manager import ProviderManager


class UnmuteAction(Action):
    """
    Action para quitar el silencio de Windows.
    """

    name = "system.unmute"

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

        try:
            result = await self._provider_manager.execute(
                provider="local",
                tool="windows.unmute",
                parameters={},
            )
        except Exception as exc:
            context.add_error(
                f"Failed to unmute system: {exc}"
            )
            return

        #
        # Estado del sistema
        #

        context.add_result(
            "muted",
            False,
        )

        context.add_result(
            "status",
            "unmuted",
        )

        #
        # Resultado original del provider
        #

        context.add_result(
            "result",
            result,
        )
