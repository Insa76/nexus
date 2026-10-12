from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from providers.provider_manager import ProviderManager


class GetVolumeAction(Action):
    """
    Action para consultar el volumen
    maestro de Windows.
    """

    name = "system.get_volume"

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
                tool="windows.get_volume",
                parameters={},
            )
        except Exception as exc:
            context.add_error(
                f"Failed to get volume: {exc}"
            )
            return

        context.add_result(
            "volume",
            result,
        )

        context.add_result(
            "status",
            "read",
        )
