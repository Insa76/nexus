from __future__ import annotations

from typing import Any, Callable
from uuid import uuid4

from planner.intent import Intent
from planner.objective import (
    Objective,
    ObjectiveStatus,
)
from planner.plan import (
    ExecutionPlan,
    PlanStep,
)


class Planner:
    """
    Convierte un Intent en un ExecutionPlan.

    El Planner consulta el catálogo de herramientas
    para resolver las capacidades disponibles.

    No conoce las implementaciones concretas de
    las Actions.

    Las relaciones entre pasos se determinan a partir
    del contrato de artifacts:

        produces → salida de un paso
        consumes → entrada de otro paso

    El Planner no asume que un paso depende
    necesariamente del paso anterior.
    """

    def __init__(
        self,
        tool_resolver: Callable[[str], Any] | None = None,
    ) -> None:

        self._tool_resolver = tool_resolver

    def create_plan(
        self,
        objective: Objective,
        intent: Intent,
    ) -> ExecutionPlan:

        objective.status = (
            ObjectiveStatus.PLANNING
        )

        plan = ExecutionPlan(
            objective_id=objective.id,
        )

        #
        # Determinar las intenciones que forman
        # el plan.
        #

        if intent.is_compound:

            intents = intent.sub_intents

        else:

            intents = [intent]

        #
        # Resolver las herramientas.
        #

        resolved_tools: list[
            tuple[Intent, Any]
        ] = []

        for sub_intent in intents:

            tool = None

            if self._tool_resolver is not None:

                tool = self._tool_resolver(
                    sub_intent.action
                )

                if tool is None:

                    objective.status = (
                        ObjectiveStatus.FAILED
                    )

                    plan.metadata = {
                        "error": (
                            "Tool not available: "
                            f"{sub_intent.action}"
                        ),
                    }

                    return plan

            resolved_tools.append(
                (
                    sub_intent,
                    tool,
                )
            )

        #
        # Crear todos los pasos.
        #

        for sub_intent, tool in resolved_tools:

            produces: list[str] = []

            consumes: list[str] = []

            if tool is not None:

                produces = list(
                    getattr(
                        tool,
                        "produces",
                        [],
                    )
                )

                consumes = list(
                    getattr(
                        tool,
                        "consumes",
                        [],
                    )
                )

            step = PlanStep(
                id=str(uuid4()),
                name=sub_intent.action,
                description=sub_intent.original_text,
                action=sub_intent.action,
                metadata=sub_intent.parameters.copy(),
                depends_on=[],
                produces=produces,
                consumes=consumes,
            )

            plan.steps.append(
                step
            )

        #
        # Resolver las dependencias mediante
        # produces / consumes.
        #

        self._resolve_dependencies(
            plan
        )

        #
        # Validar la estructura del plan.
        #

        validation_error = (
            self._validate_plan_structure(
                plan
            )
        )

        if validation_error is not None:

            objective.status = (
                ObjectiveStatus.FAILED
            )

            plan.metadata = {
                "error": validation_error,
            }

            return plan

        #
        # Validar el grafo de dependencias.
        #

        graph_error = (
            self._validate_dependency_graph(
                plan
            )
        )

        if graph_error is not None:

            objective.status = (
                ObjectiveStatus.FAILED
            )

            plan.metadata = {
                "error": graph_error,
            }

            return plan

        #
        # Un plan sin pasos no puede ejecutarse.
        #

        if not plan.steps:

            objective.status = (
                ObjectiveStatus.FAILED
            )

            plan.metadata = {
                "error": (
                    "No executable steps generated."
                ),
            }

            return plan

        objective.status = (
            ObjectiveStatus.READY
        )

        return plan

    def _resolve_dependencies(
        self,
        plan: ExecutionPlan,
    ) -> None:
        """
        Construye las dependencias del plan
        mediante los artifacts.

        Un paso depende de otro cuando consume
        un artifact producido por ese otro paso.

        La dependencia se determina únicamente
        mediante produces / consumes y no depende
        de la posición de los pasos dentro del plan.
        """

        for step in plan.steps:

            if not step.consumes:

                continue

            for candidate in plan.steps:

                #
                # El propio paso no puede ser
                # su propia dependencia.
                #

                if candidate.id == step.id:

                    continue

                #
                # Comprobar relación artifact.
                #

                if not self._produces_required_artifact(
                    candidate,
                    step,
                ):

                    continue

                #
                # Agregar dependencia.
                #

                if candidate.id not in step.depends_on:

                    step.depends_on.append(
                        candidate.id
                    )

            #
            # Orden estable para facilitar
            # debugging y serialización.
            #

            step.depends_on.sort()

    @staticmethod
    def _validate_plan_structure(
        plan: ExecutionPlan,
    ) -> str | None:
        """
        Valida la estructura de artifacts del plan.

        Cada artifact consumido debe tener exactamente
        un productor dentro del mismo plan.

        No se permite:

        - un artifact requerido sin productor;
        - un artifact requerido con múltiples
          productores posibles.

        Los pasos que no consumen artifacts no requieren
        ninguna validación adicional en esta etapa.
        """

        for step in plan.steps:

            if not step.consumes:

                continue

            for artifact in step.consumes:

                producers = [
                    candidate
                    for candidate in plan.steps
                    if candidate.id != step.id
                    and artifact in candidate.produces
                ]

                if not producers:

                    return (
                        "Missing producer for artifact: "
                        f"{artifact}"
                    )

                if len(producers) > 1:

                    return (
                        "Ambiguous producer for artifact: "
                        f"{artifact}"
                    )

        return None

    @staticmethod
    def _validate_dependency_graph(
        plan: ExecutionPlan,
    ) -> str | None:
        """
        Valida que el grafo de dependencias
        sea acíclico.

        Cada dependencia apunta desde un paso
        consumidor hacia el paso que debe ejecutarse
        previamente.

        Un ciclo significa que no existe un orden
        válido de ejecución para completar el plan.
        """

        step_ids = {
            step.id
            for step in plan.steps
        }

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(step_id: str) -> bool:

            if step_id in visiting:

                return True

            if step_id in visited:

                return False

            visiting.add(
                step_id
            )

            step = next(
                (
                    candidate
                    for candidate in plan.steps
                    if candidate.id == step_id
                ),
                None,
            )

            if step is not None:

                for dependency_id in step.depends_on:

                    #
                    # Las dependencias ya fueron
                    # construidas a partir de pasos
                    # existentes. Este control evita
                    # que una referencia inválida
                    # sea tratada como un ciclo.
                    #

                    if dependency_id not in step_ids:

                        continue

                    if visit(
                        dependency_id
                    ):

                        return True

            visiting.remove(
                step_id
            )

            visited.add(
                step_id
            )

            return False

        for step in plan.steps:

            if visit(step.id):

                return (
                    "Cyclic dependency detected."
                )

        return None

    @staticmethod
    def _produces_required_artifact(
        producer: PlanStep,
        consumer: PlanStep,
    ) -> bool:
        """
        Determina si el productor genera al menos
        uno de los artifacts que necesita el consumidor.
        """

        return any(
            artifact in consumer.consumes
            for artifact in producer.produces
        )
