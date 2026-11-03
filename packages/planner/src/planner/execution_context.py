
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from planner.objective import (
    Objective,
    ObjectiveStatus,
)

from planner.plan import (
    ExecutionPlan,
    StepStatus,
)


class ExecutionContext(BaseModel):
    """
    Contexto completo de ejecución de un Objective.

    Todos los módulos del sistema trabajan sobre este
    objeto compartido.

    Mantiene:

    - identidad del actor
    - variables
    - artifacts
    - resultados
    - errores
    - estado del Objective
    - estado de cada PlanStep
    - posición actual del plan
    - evidencia individual de cada Step

    También permite validar las dependencias declaradas
    entre los pasos del plan.
    """

    objective: Objective

    plan: ExecutionPlan

    # Identidad del actor que origina la ejecución.
    # No se asignan privilegios automáticamente.
    actor_id: str | None = None

    actor_type: str | None = None

    # Solicitud original asociada al plan; se conserva en checkpoints.
    request_text: str = ""

    variables: dict[str, Any] = Field(
        default_factory=dict
    )

    artifacts: dict[str, Any] = Field(
        default_factory=dict
    )

    results: dict[str, Any] = Field(
        default_factory=dict
    )

    errors: list[str] = Field(
        default_factory=list
    )

    current_step: int = 0

    finished: bool = False

    #
    # Evidencia producida por cada Step.
    #
    # La clave es el ID del PlanStep.
    #
    # Ejemplo:
    #
    # {
    #     "step-1": {
    #         "action": "system.open_app",
    #         "status": "completed",
    #         "results": {...},
    #         "artifacts": {...},
    #     }
    # }
    #

    step_evidence: dict[str, dict[str, Any]] = Field(
        default_factory=dict
    )

    def current_plan_step(
        self,
    ) -> Any | None:
        """
        Devuelve el paso actualmente seleccionado.
        """

        if self.finished:
            return None

        if self.current_step >= len(self.plan.steps):
            return None

        return self.plan.steps[self.current_step]

    def get_step(
        self,
        step_id: str,
    ) -> Any | None:
        """
        Busca un paso del plan por su ID.
        """

        for step in self.plan.steps:
            if step.id == step_id:
                return step

        return None

    def validate_step_dependencies(
        self,
        step: Any,
    ) -> tuple[bool, list[str]]:
        """
        Valida las dependencias declaradas por un paso.
        """

        missing: list[str] = []

        for dependency_id in getattr(
            step,
            "depends_on",
            [],
        ):
            dependency = self.get_step(dependency_id)

            if dependency is None:
                missing.append(dependency_id)
                continue

            if dependency.status != StepStatus.COMPLETED:
                missing.append(dependency_id)

        return (
            len(missing) == 0,
            missing,
        )

    def validate_step_inputs(
        self,
        step: Any,
    ) -> tuple[bool, list[str]]:
        """
        Valida que todos los artifacts declarados
        por el paso como consumidos estén disponibles.
        """

        missing: list[str] = []

        for artifact_name in getattr(
            step,
            "consumes",
            [],
        ):
            if not self.has_artifact(artifact_name):
                missing.append(artifact_name)

        return (
            len(missing) == 0,
            missing,
        )

    def record_step_evidence(
        self,
        step: Any,
        *,
        status: str,
        results_before: dict[str, Any],
        artifacts_before: dict[str, Any],
    ) -> None:
        """
        Registra evidencia específica producida por un Step.

        Solamente guarda los cambios producidos durante
        la ejecución de ese Step.

        Esto evita atribuir a un paso evidencia generada
        anteriormente por otro paso del plan.
        """

        result_delta = {
            key: value
            for key, value in self.results.items()
            if (
                key not in results_before
                or results_before[key] != value
            )
        }

        artifact_delta = {
            key: value
            for key, value in self.artifacts.items()
            if (
                key not in artifacts_before
                or artifacts_before[key] != value
            )
        }

        self.step_evidence[step.id] = {
            "step_id": step.id,
            "action": step.action,
            "status": status,
            "results": result_delta,
            "artifacts": artifact_delta,
        }

    def get_step_evidence(
        self,
        step_id: str,
    ) -> dict[str, Any] | None:
        """
        Devuelve la evidencia registrada para un Step.
        """

        return self.step_evidence.get(step_id)

    def all_step_evidence(
        self,
    ) -> dict[str, dict[str, Any]]:
        """
        Devuelve toda la evidencia de los Steps.
        """

        return dict(self.step_evidence)

    def mark_step_running(
        self,
    ) -> None:
        """
        Marca el paso actual como RUNNING.
        """

        step = self.current_plan_step()

        if step is None:
            return

        step.status = StepStatus.RUNNING
        self.objective.status = ObjectiveStatus.RUNNING

    def mark_step_failed(
        self,
        error: str | None = None,
    ) -> None:
        """
        Marca el paso actual como FAILED
        y detiene el plan.
        """

        step = self.current_plan_step()

        if step is not None:
            step.status = StepStatus.FAILED

        if error:
            self.add_error(error)

        self.objective.status = ObjectiveStatus.FAILED
        self.finished = True
        self.plan.completed = False

    def next_step(
        self,
    ) -> None:
        """
        Completa el paso actual y avanza
        al siguiente.

        Si existen errores, el plan se detiene.
        """

        if self.finished:
            return

        step = self.current_plan_step()

        if step is not None:
            if self.has_errors():
                step.status = StepStatus.FAILED
                self.objective.status = ObjectiveStatus.FAILED
                self.finished = True
                self.plan.completed = False
                return

            step.status = StepStatus.COMPLETED

        self.current_step += 1

        if self.current_step >= len(self.plan.steps):
            self.finished = True
            self.plan.completed = True
            self.objective.status = ObjectiveStatus.COMPLETED

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
        return self.variables.get(name, default)

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

    def get_artifact(
        self,
        name: str,
        default: Any = None,
    ) -> Any:
        return self.artifacts.get(name, default)

    def has_artifact(
        self,
        name: str,
    ) -> bool:
        return name in self.artifacts

    def add_error(
        self,
        error: str,
    ) -> None:
        self.errors.append(error)

    def has_errors(
        self,
    ) -> bool:
        """
        Indica si durante la ejecución
        se produjo al menos un error.
        """

        return len(self.errors) > 0
