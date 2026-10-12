from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from providers.provider_manager import ProviderManager


class MuteAction(Action):
    """
    Action para silenciar Windows.
    """

    name = "system.mute"

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
                tool="windows.mute",
                parameters={},
            )
        except Exception as exc:
            context.add_error(
                f"Failed to mute system: {exc}"
            )
            return

        #
        # Estado del sistema
        #

        context.add_result(
            "muted",
            True,
        )

        context.add_result(
            "status",
            "muted",
        )

        #
        # Resultado original del provider
        #

        context.add_result(
            "result",
            result,
        )
