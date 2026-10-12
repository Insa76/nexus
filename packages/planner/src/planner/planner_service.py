from __future__ import annotations

from planner.objective import Objective
from planner.plan import ExecutionPlan
from planner.planner import Planner


class PlannerService:
    """
    Fachada del sistema de planificación.

    Expone una interfaz simple para que el Runtime
    solicite planes sin conocer la implementación
    del Planner.
    """

    def __init__(self, planner: Planner) -> None:

        self._planner = planner

    def create_plan(
        self,
        objective: Objective,
    ) -> ExecutionPlan:
        """
        Genera un plan para un objetivo.
        """

        return self._planner.create_plan(
            objective
        )
