from __future__ import annotations

from uuid import uuid4

from packages.planner.src.planner.intent import Intent
from packages.planner.src.planner.objective import Objective


class ObjectiveFactory:
    """
    Responsable de crear Objectives
    a partir de un Intent.
    """

    def create(
        self,
        intent: Intent,
    ) -> Objective:

        return Objective(

            id=str(uuid4()),

            title=intent.action,

            metadata=intent.parameters.copy(),

        )