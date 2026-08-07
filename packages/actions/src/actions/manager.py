from __future__ import annotations

from planner.execution_context import ExecutionContext

from actions.registry import ActionRegistry


class ActionManager:

    def __init__(
        self,
        registry: ActionRegistry,
    ):

        self._registry = registry

    async def execute(
        self,
        context: ExecutionContext,
    ) -> None:

        step = context.current_plan_step()

        if step is None:

            return

        action = self._registry.get(
            step.action
        )

        await action.execute(
            context,
            step,
        )

        context.next_step()