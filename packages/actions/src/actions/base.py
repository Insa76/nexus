from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from planner.execution_context import ExecutionContext
from planner.plan import PlanStep


class Action(ABC):
    """
    Clase base para todas las Actions de NEXUS.
    """

    name: str

    description: str = ""

    parameters: dict[str, Any] = {}

    internal: bool = False

    produces: list[str] = []

    consumes: list[str] = []

    @abstractmethod
    async def execute(
        self,
        context: ExecutionContext,
        step: PlanStep,
    ) -> None:
        ...
