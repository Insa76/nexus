from __future__ import annotations

from planner.execution_context import ExecutionContext

from runtime.execution_result import ExecutionResult


class Executor:
    """
    Ejecuta un ExecutionContext completo.

    El Executor no conoce las Actions.
    Solamente coordina el Runtime.
    """

    def __init__(
        self,
        runtime,
    ) -> None:

        self.runtime = runtime

    async def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:

        result = ExecutionResult()

        if self.runtime.action_manager is None:

            result.success = False
            result.errors.append(
                "ActionManager has not been configured."
            )

            return result

        while True:

            step = context.current_plan_step()

            if step is None:
                break

            await self.runtime.action_manager.execute(
                context
            )

        result.success = len(
            context.errors
        ) == 0

        result.data = context.results.copy()

        result.errors.extend(
            context.errors
        )

        return result