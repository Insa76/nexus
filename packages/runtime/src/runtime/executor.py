from __future__ import annotations

import time

from planner.execution_context import ExecutionContext
from planner.objective import ObjectiveStatus
from planner.plan import StepStatus
from runtime.execution_result import ExecutionResult


class Executor:
    """
    Ejecuta un ExecutionPlan respetando sus dependencias.

    El Executor es responsable de determinar el estado
    global del Plan. El ActionManager solamente ejecuta
    y actualiza el estado de cada Step.
    """

    def __init__(self, runtime):
        self.runtime = runtime

    async def execute(
        self,
        context: ExecutionContext,
    ) -> ExecutionResult:

        start = time.perf_counter()

        result = ExecutionResult()

        #
        # Verificar infraestructura de ejecución.
        #

        if self.runtime.action_manager is None:

            result.success = False

            result.message = (
                "ActionManager has not been configured."
            )

            result.metadata = (
                self._build_metadata(context)
            )

            result.execution_time = (
                time.perf_counter() - start
            )

            return result

        # Persistir el inicio antes de ejecutar cualquier acción con efectos.
        execution_store = getattr(self.runtime, "execution_store", None)
        if execution_store is not None:
            execution_store.begin(context)

        #
        # Ejecución del grafo.
        #

        while not context.finished:

            #
            # Si todos los steps terminaron,
            # el Plan terminó correctamente.
            #

            if self._all_steps_completed(
                context
            ):

                context.plan.completed = True

                context.objective.status = (
                    ObjectiveStatus.COMPLETED
                )

                context.finished = True

                break

            #
            # Buscar cualquier step pendiente
            # cuyas dependencias estén satisfechas.
            #

            step_index = (
                self._find_next_executable_step(
                    context
                )
            )

            #
            # No existe ningún step ejecutable.
            #

            if step_index is None:

                pending_steps = [
                    step
                    for step in context.plan.steps
                    if step.status
                    == StepStatus.PENDING
                ]

                #
                # Si todavía hay steps pendientes,
                # el grafo está bloqueado.
                #

                if pending_steps:

                    blocked = []

                    for step in pending_steps:

                        (
                            dependencies_ok,
                            missing_dependencies,
                        ) = (
                            context.validate_step_dependencies(
                                step
                            )
                        )

                        if not dependencies_ok:

                            blocked.append(
                                {
                                    "step": step.id,
                                    "missing_dependencies": (
                                        missing_dependencies
                                    ),
                                }
                            )

                    error = (
                        "Execution plan is blocked: "
                        f"{blocked}"
                    )

                    context.add_error(
                        error
                    )

                    context.objective.status = (
                        ObjectiveStatus.FAILED
                    )

                    context.finished = True

                    context.plan.completed = False

                break

            #
            # El Executor selecciona el step.
            #
            # current_step es solamente un puntero
            # operativo hacia el step seleccionado.
            #

            context.current_step = step_index

            # El checkpoint previo identifica el paso que estaba por comenzar.
            # Si el proceso cae durante la acción, nunca se reejecuta en automático.
            if execution_store is not None:
                execution_store.checkpoint(context)

            #
            # ActionManager ejecuta el step.
            #

            await self.runtime.action_manager.execute(
                context
            )

            if execution_store is not None:
                execution_store.checkpoint(context)

            #
            # Si la ejecución produjo un error,
            # el plan y el objetivo fallaron.
            #

            if context.has_errors():

                context.plan.completed = False

                context.objective.status = (
                    ObjectiveStatus.FAILED
                )

                context.finished = True

                break

            #
            # El ActionManager actualizó el estado
            # del step. Volvemos a evaluar el grafo
            # completo en la siguiente iteración.
            #

            completed_count = sum(
                1
                for step in context.plan.steps
                if step.status
                == StepStatus.COMPLETED
            )

            #
            # current_step representa ahora la cantidad
            # de steps completados, no una condición
            # de finalización del Plan.
            #

            context.current_step = (
                completed_count
            )

            #
            # Comprobar nuevamente si todo el grafo
            # terminó.
            #

            if self._all_steps_completed(
                context
            ):

                context.plan.completed = True

                context.objective.status = (
                    ObjectiveStatus.COMPLETED
                )

                context.finished = True

        #
        # Resultado final.
        #

        result.success = (
            not context.has_errors()
            and context.plan.completed
            and self._all_steps_completed(
                context
            )
        )

        result.output = dict(
            context.results
        )

        result.artifacts = dict(
            context.artifacts
        )

        if context.errors:

            result.message = (
                "\n".join(
                    context.errors
                )
            )

        else:

            result.message = (
                "Execution completed successfully."
            )

        result.metadata = (
            self._build_metadata(context)
        )

        result.execution_time = (
            time.perf_counter() - start
        )

        if execution_store is not None:
            execution_store.finish(
                context,
                success=result.success,
                error=result.message if not result.success else None,
            )

        return result

    @staticmethod
    def _find_next_executable_step(
        context: ExecutionContext,
    ) -> int | None:

        for index, step in enumerate(
            context.plan.steps
        ):

            if step.status != StepStatus.PENDING:
                continue

            (
                dependencies_ok,
                _,
            ) = context.validate_step_dependencies(
                step
            )

            if dependencies_ok:
                return index

        return None

    @staticmethod
    def _all_steps_completed(
        context: ExecutionContext,
    ) -> bool:

        if not context.plan.steps:
            return False

        return all(
            step.status
            == StepStatus.COMPLETED
            for step in context.plan.steps
        )

    @staticmethod
    def _build_metadata(
        context: ExecutionContext,
    ) -> dict:

        metadata = {
            "objective_id": context.objective.id,
            "objective_status": (
                context.objective.status.value
            ),
            "plan_completed": (
                context.plan.completed
            ),
            "current_step": (
                context.current_step
            ),
            "step_count": (
                len(context.plan.steps)
            ),
            "errors": list(
                context.errors
            ),
            "step_evidence": (
                context.all_step_evidence()
            ),
        }

        if context.variables:

            metadata["variables"] = dict(
                context.variables
            )

        return metadata
