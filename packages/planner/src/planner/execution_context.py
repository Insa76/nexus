from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from planner.objective import Objective
from planner.plan import ExecutionPlan


class ExecutionContext(BaseModel):
    """
    Contexto completo de ejecución de un Objective.

    Todos los módulos del sistema trabajan sobre este
    objeto compartido.

    De esta forma evitamos pasar decenas de parámetros
    entre componentes.
    """

    objective: Objective

    plan: ExecutionPlan

    variables: dict[str, Any] = Field(default_factory=dict)

    artifacts: dict[str, Any] = Field(default_factory=dict)

    results: dict[str, Any] = Field(default_factory=dict)

    errors: list[str] = Field(default_factory=list)

    current_step: int = 0

    finished: bool = False

    def current_plan_step(self):

        if self.current_step >= len(self.plan.steps):

            return None

        return self.plan.steps[self.current_step]

    def next_step(self):

        self.current_step += 1

        if self.current_step >= len(self.plan.steps):

            self.finished = True

    def set_variable(
        self,
        name: str,
        value: Any,
    ) -> None:

        self.variables[name] = value

    def get_variable(
        self,
        name: str,
        default: Any = None,
    ) -> Any:

        return self.variables.get(
            name,
            default,
        )

    def add_result(
        self,
        name: str,
        value: Any,
    ) -> None:

        self.results[name] = value

    def add_artifact(
        self,
        name: str,
        artifact: Any,
    ) -> None:

        self.artifacts[name] = artifact

    def add_error(
        self,
        error: str,
    ) -> None:

        self.errors.append(error)

    def has_errors(self) -> bool:
        """
        Indica si durante la ejecución se produjo
        al menos un error.
        """

        return len(self.errors) > 0    