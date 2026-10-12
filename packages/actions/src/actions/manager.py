
from __future__ import annotations

from planner.execution_context import ExecutionContext
from planner.objective import ObjectiveStatus
from planner.plan import StepStatus

from actions.registry import ActionRegistry
from security import ActionAuthorization, Actor, ActorType


class ActionManager:
    """
    Ejecuta Actions a partir del ExecutionContext.

    El ActionManager coordina la ejecución del paso
    actual y mantiene sincronizado el estado del
    Objective con el resultado real de la Action.

    También registra la evidencia producida
    específicamente por cada PlanStep.

    La autorización, cuando está configurada,
    se comprueba antes de ejecutar cada Action.

    No decide cuándo finaliza globalmente el Plan.
    Esa responsabilidad pertenece al Executor.
    """

    def __init__(
        self,
        registry: ActionRegistry,
        action_authorization: ActionAuthorization | None = None,
    ) -> None:
        self._registry = registry
        self._action_authorization = action_authorization

    async def execute(
        self,
        context: ExecutionContext,
    ) -> None:
        """
        Ejecuta el paso actual del plan.

        Si Security está configurado, la acción debe
        estar autorizada antes de llegar a execute().
        """

        step = context.current_plan_step()

        if step is None:
            return

        #
        # Paso en ejecución.
        #

        step.status = StepStatus.RUNNING
        context.objective.status = ObjectiveStatus.RUNNING

        #
        # Capturamos el estado previo para registrar
        # únicamente la evidencia producida por este paso.
        #

        results_before = context.results.copy()
        artifacts_before = context.artifacts.copy()

        #
        # Resolver Action.
        #

        try:
            action = self._registry.get(step.action)

        except Exception as exc:
            error = (
                f"Failed to resolve action "
                f"'{step.action}': {exc}"
            )

            step.status = StepStatus.FAILED
            context.add_error(error)

            context.record_step_evidence(
                step,
                status="failed",
                results_before=results_before,
                artifacts_before=artifacts_before,
            )

            context.objective.status = ObjectiveStatus.FAILED
            context.finished = True
            context.plan.completed = False
            return

        #
        # Autorizar antes de ejecutar la Action.
        #

        if self._action_authorization is not None:
            actor = None

            if context.actor_id and context.actor_type:
                try:
                    actor = Actor(
                        id=context.actor_id,
                        actor_type=ActorType(context.actor_type),
                    )
                except (ValueError, TypeError):
                    actor = None

            allowed = (
                actor is not None
                and self._action_authorization.is_allowed(
                    actor,
                    step.action,
                )
            )

            if not allowed:
                actor_description = (
                    context.actor_id
                    if context.actor_id
                    else "unknown"
                )

                error = (
                    "Authorization denied: actor "
                    f"'{actor_description}' cannot execute "
                    f"action '{step.action}'."
                )

                step.status = StepStatus.FAILED
                context.add_error(error)

                context.record_step_evidence(
                    step,
                    status="failed",
                    results_before=results_before,
                    artifacts_before=artifacts_before,
                )

                context.step_evidence[step.id]["authorization"] = {
                    "allowed": False,
                    "actor_id": context.actor_id,
                    "action": step.action,
                }

                context.objective.status = ObjectiveStatus.FAILED
                context.finished = True
                context.plan.completed = False
                return

        #
        # Ejecutar Action.
        #

        try:
            await action.execute(
                context,
                step,
            )

        except Exception as exc:
            error = (
                f"Action '{step.action}' "
                f"failed: {exc}"
            )

            step.status = StepStatus.FAILED
            context.add_error(error)

            context.record_step_evidence(
                step,
                status="failed",
                results_before=results_before,
                artifacts_before=artifacts_before,
            )

            context.objective.status = ObjectiveStatus.FAILED
            context.finished = True
            context.plan.completed = False
            return

        #
        # La Action puede haber capturado una excepción
        # internamente y registrado un error en el contexto.
        #

        if context.has_errors():
            step.status = StepStatus.FAILED

            context.record_step_evidence(
                step,
                status="failed",
                results_before=results_before,
                artifacts_before=artifacts_before,
            )

            context.objective.status = ObjectiveStatus.FAILED
            context.finished = True
            context.plan.completed = False
            return

        #
        # Registrar evidencia real producida por el Step.
        #

        context.record_step_evidence(
            step,
            status="completed",
            results_before=results_before,
            artifacts_before=artifacts_before,
        )

        #
        # La Action terminó correctamente.
        # El Executor determina la finalización global.
        #

        step.status = StepStatus.COMPLETED
