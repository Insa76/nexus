from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from planner.execution_context import ExecutionContext
from planner.plan import PlanStep


class Action(ABC):
    """
    Clase base para todas las acciones de NEXUS.
    """

    name: str

    @abstractmethod
    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:
        ...