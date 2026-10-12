from __future__ import annotations

from actions.base import Action

from planner.plan import PlanStep
from planner.execution_context import ExecutionContext

from providers.provider_manager import ProviderManager


class ProcessListAction(Action):
    """
    Action para obtener los procesos
    actualmente ejecutándose.
    """

    name = "system.process_list"

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

            processes = await self._provider_manager.execute(
                provider="local",
                tool="windows.list_processes",
                parameters={},
            )

        except Exception as exc:

            context.add_error(
                f"Failed to list processes: {exc}"
            )

            return

        context.add_result(
            "processes",
            processes,
        )

        context.add_result(
            "count",
            len(processes),
        )

        context.add_result(
            "status",
            "ok",
        )
