from __future__ import annotations

from actions.base import Action

from planner.plan import PlanStep

from planner.execution_context import ExecutionContext

from adapters.windows.process_manager import (

    WindowsProcessManager,

)


class ProcessListAction(Action):

    name = "system.process_list"

    def __init__(self):

        self._adapter = WindowsProcessManager()

    async def execute(

        self,

        context: ExecutionContext,

        step: PlanStep,

    ) -> None:

        processes = self._adapter.list_processes()

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