from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from providers.provider_manager import ProviderManager


class GetMuteAction(Action):
    """
    Action para consultar el estado actual
    de silencio de Windows.
    """

    name = "system.get_mute"

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
                tool="windows.get_mute",
                parameters={},
            )

        except Exception as exc:

            context.add_error(
                f"Failed to get mute state: {exc}"
            )

            return

        context.add_result(
            "muted",
            bool(result),
        )

        context.add_result(
            "status",
            "read",
        )
