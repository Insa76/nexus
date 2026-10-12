from __future__ import annotations

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from actions.base import Action

from providers.provider_manager import ProviderManager


class SetVolumeAction(Action):
    """
    Action para establecer el volumen
    maestro de Windows.
    """

    name = "system.set_volume"

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

        level = step.metadata.get("level")

        if level is None:
            context.add_error(
                "No volume level specified."
            )
            return

        try:
            level = float(level)
        except (TypeError, ValueError):
            context.add_error(
                "Volume level must be numeric."
            )
            return

        if level < 0 or level > 100:
            context.add_error(
                "Volume level must be between 0 and 100."
            )
            return

        try:
            result = await self._provider_manager.execute(
                provider="local",
                tool="windows.set_volume",
                parameters={
                    "level": level,
                },
            )
        except Exception as exc:
            context.add_error(
                f"Failed to set volume: {exc}"
            )
            return

        context.add_result(
            "volume",
            result,
        )

        context.add_result(
            "status",
            "set",
        )
